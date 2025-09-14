from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.cart import CartService
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartItemResponse, CartSummary
from app.core.database import get_db

router = APIRouter(tags=["cart"])
security = HTTPBearer()


@router.post("/add", response_model=CartItemResponse, status_code=201, summary="Add item to cart")
async def add_to_cart(
    cart_data: CartItemAdd,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add item to cart. If item already exists, quantity will be increased."""
    cart_item = await CartService.add_item_to_cart(db, current_user["user_id"], cart_data)
    if not cart_item:
        raise HTTPException(status_code=400, detail="Product not found or inactive")
    
    subtotal = cart_item.quantity * cart_item.product.price
    
    return CartItemResponse(
        cart_item_id=cart_item.cart_item_id,
        user_id=cart_item.user_id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity,
        added_at=cart_item.added_at,
        updated_at=cart_item.updated_at,
        product=cart_item.product,
        subtotal=subtotal
    )

@router.get("/", response_model=CartSummary, summary="Get cart items")
async def get_cart(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all items in user's cart with summary information."""
    cart_items = await CartService.get_user_cart(db, current_user["user_id"])
    cart_summary = await CartService.calculate_cart_summary(cart_items)
    
    response_items = []
    for item in cart_items:
        subtotal = item.quantity * item.product.price
        response_items.append(CartItemResponse(
            cart_item_id=item.cart_item_id,
            user_id=item.user_id,
            product_id=item.product_id,
            quantity=item.quantity,
            added_at=item.added_at,
            updated_at=item.updated_at,
            product=item.product,
            subtotal=subtotal
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
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update cart item quantity."""
    cart_item = await CartService.update_cart_item(db, cart_item_id, current_user["user_id"], cart_data)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    subtotal = cart_item.quantity * cart_item.product.price
    
    return CartItemResponse(
        cart_item_id=cart_item.cart_item_id,
        user_id=cart_item.user_id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity,
        added_at=cart_item.added_at,
        updated_at=cart_item.updated_at,
        product=cart_item.product,
        subtotal=subtotal
    )

@router.delete("/{cart_item_id}", status_code=204, summary="Remove item from cart")
async def remove_cart_item(
    cart_item_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove item from cart."""
    success = await CartService.remove_cart_item(db, cart_item_id, current_user["user_id"])
    if not success:
        raise HTTPException(status_code=404, detail="Cart item not found")