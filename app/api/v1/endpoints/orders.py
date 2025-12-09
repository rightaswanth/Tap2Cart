from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.dependencies import get_current_admin_user, get_current_user
from app.services.orders import OrderService
from app.schemas.orders import (
    OrderResponse, OrderCreate, OrderUpdate, OrderStatusUpdate, OrderSummary
)
from app.core.database import get_db  # AsyncSession dependency

router = APIRouter(tags=["orders"])
security = HTTPBearer()


# -------------------- ORDERS --------------------

@router.get("/", response_model=List[OrderResponse], summary="Get orders")
async def get_orders(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's orders.
    """
    orders = await OrderService.get_orders(
        db, 
        user_id=user_id, 
        is_admin=False,
        skip=skip, 
        limit=limit
    )
    return orders


@router.get("/{order_id}", response_model=OrderResponse, summary="Get specific order")
async def get_order(
    order_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    order = await OrderService.get_order_by_id(
        db, 
        order_id, 
        user_id=user_id, 
        is_admin=False
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", response_model=OrderResponse, status_code=201, summary="Create new order")
async def create_order(
    order_data: OrderCreate,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    order = await OrderService.create_order(db, user_id, order_data)
    if not order:
        raise HTTPException(
            status_code=400, 
            detail="Failed to create order. Check if all products exist and are active."
        )
    return order


@router.put("/{order_id}", response_model=OrderResponse, summary="Update order")
async def update_order(
    order_id: str,
    order_data: OrderUpdate,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    order = await OrderService.update_order(
        db, 
        order_id, 
        order_data, 
        user_id=user_id, 
        is_admin=False
    )
    if not order:
        raise HTTPException(
            status_code=404, 
            detail="Order not found or cannot be updated"
        )
    return order


@router.delete("/{order_id}", status_code=204, summary="Cancel order")
async def cancel_order(
    order_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    success = await OrderService.cancel_order(
        db, 
        order_id, 
        user_id=user_id, 
        is_admin=False
    )
    if not success:
        raise HTTPException(
            status_code=404, 
            detail="Order not found or cannot be cancelled"
        )
    return


@router.get("/{order_id}/status", summary="Get order status")
async def get_order_status(
    order_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    status_info = await OrderService.get_order_status(
        db, 
        order_id, 
        user_id=user_id, 
        is_admin=False
    )
    if not status_info:
        raise HTTPException(status_code=404, detail="Order not found")
    return status_info


@router.put("/{order_id}/status", response_model=OrderResponse, summary="Update order status (Admin)")
async def update_order_status(
    order_id: str,
    status_data: OrderStatusUpdate,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    order = await OrderService.update_order_status(db, order_id, status_data)
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
