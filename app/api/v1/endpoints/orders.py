from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.dependencies import get_current_admin_user, get_current_active_user, get_current_user_optional
from app.services.orders import order_service
from app.schemas.orders import (
    OrderResponse, OrderCreate, OrderUpdate, OrderStatusUpdate, OrderSummary, OrderTrackingResponse
)
from app.core.database import get_db  # AsyncSession dependency

router = APIRouter(tags=["orders"])
security = HTTPBearer()



@router.get("/", response_model=List[OrderResponse], summary="Get orders")
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's orders.
    """
    orders = await order_service.get_multi_by_user(
        db, 
        user_id=current_user.user_id, 
        is_admin=False,
        skip=skip, 
        limit=limit
    )
    return orders


@router.get("/{order_id}", response_model=OrderResponse, summary="Get specific order")
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    order = await order_service.get(
        db, 
        id=order_id, 
        user_id=current_user.user_id, 
        is_admin=False
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", response_model=OrderResponse, status_code=201, summary="Create new order")
async def create_order(
    order_data: OrderCreate,
    current_user: Optional[dict] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.user_id if current_user else None
    order = await order_service.create_order(db, user_id, order_data)
    if not order:
        raise HTTPException(
            status_code=400, 
            detail="Failed to create order. Check if all products exist and are active."
        )
    return order



@router.post("/{order_id}/confirm", summary="Confirm order and payment")
async def confirm_order(
    order_id: str,
    transaction_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm order payment. 
    This triggers stock deduction and locks concurrency.
    """
    result = await order_service.confirm_order(db, order_id, transaction_id)
    
    if result["status"] == "error":
        # If it's a domain error like "Order already paid", 400 is fine. 
        # If system error/rollback, maybe 500 but service returns error status.
        raise HTTPException(status_code=400, detail=result["message"])
    elif result["status"] == "refund":
        # Return 200 with specific status or 409? 
        # User paid but stock gone. Front end needs to know to show "Refunded".
        # Let's return 200 but body indicates refund.
        return {"status": "refund_initiated", "message": result["message"]}
    
    return {"status": "confirmed", "message": result["message"]}


@router.put("/{order_id}", response_model=OrderResponse, summary="Update order")
async def update_order(
    order_id: str,
    order_data: OrderUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # First fetch the order to ensure ownership
    order = await order_service.get(
        db, 
        id=order_id, 
        user_id=current_user.user_id, 
        is_admin=False
    )
    if not order:
        raise HTTPException(
            status_code=404, 
            detail="Order not found or cannot be updated"
        )
    
    # Use generic update
    updated_order = await order_service.update(
        db,
        db_obj=order,
        obj_in=order_data
    )
    return updated_order


@router.delete("/{order_id}", status_code=204, summary="Cancel order")
async def cancel_order(
    order_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    success = await order_service.cancel_order(
        db, 
        order_id, 
        user_id=current_user.user_id, 
        is_admin=False
    )
    if not success:
         raise HTTPException(status_code=400, detail="Unable to cancel order")
    # 204 No Content returns no body
    return


@router.get("/{order_id}/status", summary="Get order status")
async def get_order_status(
    order_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    status_info = await order_service.get_order_status(
        db, 
        order_id, 
        user_id=current_user.user_id, 
        is_admin=False
    )
    if not status_info:
        raise HTTPException(status_code=404, detail="Order not found")
    return status_info


@router.get("/track/{tracking_token}", response_model=OrderTrackingResponse, summary="Track order (Public)")
async def track_order(
    tracking_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Track order using a public tracking token.
    Returns order details including status and address.
    """
    order = await order_service.get_by_tracking_token(db, tracking_token)
    
    if not order:
         raise HTTPException(status_code=404, detail="Order not found or invalid token")
    
    # Mock Delivery Steps based on status
    steps = [
        {"status": "Placed", "completed": True, "date": order.created_at},
        {"status": "Processing", "completed": order.order_status in ["Processing", "Shipped", "Delivered"], "date": None},
        {"status": "Shipped", "completed": order.order_status in ["Shipped", "Delivered"], "date": None},
        {"status": "Delivered", "completed": order.order_status == "Delivered", "date": None},
    ]
    
    # Pydantic will convert the SQLAlchemy object to the response model, 
    # but we need to inject the mock steps.
    response = OrderTrackingResponse.from_orm(order)
    response.delivery_steps = steps
    
    return response


# Admin Endpoints

@router.get("/admin/all", response_model=List[OrderResponse], summary="Get all orders (Admin)")
async def get_all_orders_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all orders in the system."""
    orders = await order_service.get_multi_by_user(
        db, is_admin=True, skip=skip, limit=limit
    )
    return orders

@router.patch("/{order_id}/status", response_model=OrderResponse, summary="Update order status (Admin)")
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update order status."""
    order = await order_service.update_order_status(db, order_id, status_update)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/user/{user_id}/orders", response_model=List[OrderSummary], summary="Get user orders (Admin)")
async def get_user_orders(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    orders = await OrderService.get_orders(db, user_id=user_id, is_admin=True, skip=skip, limit=limit)
    
    order_summaries = [
        OrderSummary(
            order_id=o.order_id,
            total_amount=o.total_amount,
            order_status=o.order_status,
            payment_status=o.payment_status,
            created_at=o.created_at,
            items_count=len(o.items)
        ) for o in orders
    ]
    
    return order_summaries
