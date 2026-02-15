from fastapi import APIRouter, Depends, HTTPException, Query
from decimal import Decimal
from typing import Optional
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.database import get_db
from app.services.cart import cart_service
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartItemResponse, CartSummary

router = APIRouter(tags=["cart"])


from app.core.dependencies import get_current_user_optional
from app.models.user import User

@router.post("/add", response_model=CartItemResponse, status_code=201, summary="Add item to cart")
async def add_to_cart(
    cart_data: CartItemAdd,
    guest_id: str = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a product to the shopping cart.

    - If user is logged in, uses user_id from token.
    - If guest, requires guest_id query parameter.
    """
    user_id = current_user.user_id if current_user else None
    
    if not user_id and not guest_id:
        raise HTTPException(status_code=400, detail="Either user (token) or guest_id (query) is required")
        
    cart_item = await cart_service.add_item_to_cart(db, user_id, cart_data, guest_id)

    if not cart_item:
        raise HTTPException(status_code=400, detail="Product not found or inactive")
    
    return CartItemResponse(
        cart_item_id=cart_item.cart_item_id,
        user_id=cart_item.user_id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity,
        added_at=cart_item.added_at,
        updated_at=cart_item.updated_at,
        product=cart_item.product,
        subtotal=cart_item.quantity * cart_item.product.price
    )

@router.get("/", response_model=CartSummary, summary="Get cart items")
async def get_cart(
    guest_id: str = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all items in user's or guest's cart with summary information.
    """

    if not current_user.user_id and not guest_id:
         return CartSummary(items=[], total_items=0, total_amount=Decimal('0.00'))

    cart_items = await cart_service.get_user_cart(db, current_user.user_id, guest_id)
    cart_summary = await cart_service.calculate_cart_summary(cart_items)
    
    response_items = []
    for item in cart_items:
        response_items.append(CartItemResponse(
            cart_item_id=item.cart_item_id,
            user_id=item.user_id,
            product_id=item.product_id,
            quantity=item.quantity,
            added_at=item.added_at,
            updated_at=item.updated_at,
            product=item.product,
            subtotal=item.quantity * item.product.price
        ))
    
    return CartSummary(
        items=response_items,
        total_items=cart_summary["total_items"],
        total_amount=cart_summary["total_amount"]
    )

@router.put("/{cart_item_id}", response_model=CartItemResponse, summary="Update cart item quantity")
async def update_cart_item(
    cart_item_id: str,
    cart_data: CartItemUpdate,
    guest_id: str = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Update cart item quantity.
    """
    if not current_user.user_id and not guest_id:
        raise HTTPException(status_code=400, detail="Either user (token) or guest_id (query) is required")

    cart_item = await cart_service.update_cart_item(db, cart_item_id, cart_data, current_user.user_id, guest_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    return CartItemResponse(
        cart_item_id=cart_item.cart_item_id,
        user_id=cart_item.user_id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity,
        added_at=cart_item.added_at,
        updated_at=cart_item.updated_at,
        product=cart_item.product,
        subtotal=cart_item.quantity * cart_item.product.price
    )

@router.delete("/{cart_item_id}", status_code=204, summary="Remove item from cart")
async def remove_cart_item(
    cart_item_id: str,
    guest_id: str = Query(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove item from cart.
    """
    if not current_user.user_id and not guest_id:
        raise HTTPException(status_code=400, detail="Either user (token) or guest_id (query) is required")

    success = await cart_service.remove_cart_item(db, cart_item_id, current_user.user_id, guest_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cart item not found")