from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
from app.models.cart import CartItem
from app.models.product import Product
from app.schemas.cart import CartItemAdd, CartItemUpdate
from typing import List, Optional
from decimal import Decimal
import datetime

class CartService:
    
    @staticmethod
    async def get_user_cart(db: AsyncSession, user_id: str) -> List[CartItem]:
        """Get all active cart items for a user."""
        query = select(CartItem).options(
            selectinload(CartItem.product)
        ).where(
            CartItem.user_id == user_id,
            CartItem.is_active == True
        ).order_by(CartItem.added_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def add_item_to_cart(db: AsyncSession, user_id: str, cart_data: CartItemAdd) -> Optional[CartItem]:
        """Add item to cart or update quantity if item already exists."""
        # Check if product exists and is active
        product_query = select(Product).where(
            Product.product_id == cart_data.product_id,
            Product.is_active == True
        )
        product_result = await db.execute(product_query)
        product = product_result.scalar_one_or_none()
        
        if not product:
            return None
        
        # Check if item already exists in cart
        existing_query = select(CartItem).options(
            selectinload(CartItem.product)
        ).where(
            CartItem.user_id == user_id,
            CartItem.product_id == cart_data.product_id,
            CartItem.is_active == True
        )
        existing_result = await db.execute(existing_query)
        existing_item = existing_result.scalar_one_or_none()
        
        if existing_item:
            # Update existing item quantity
            existing_item.quantity += cart_data.quantity
            existing_item.updated_at = datetime.datetime.utcnow()
            await db.commit()
            await db.refresh(existing_item)
            return existing_item
        else:
            # Create new cart item
            cart_item = CartItem(
                user_id=user_id,
                product_id=cart_data.product_id,
                quantity=cart_data.quantity
            )
            db.add(cart_item)
            await db.commit()
            await db.refresh(cart_item)
            # Manually set the product since we already fetched it to avoid lazy load error
            cart_item.product = product
            return cart_item
    
    @staticmethod
    async def get_cart_item(db: AsyncSession, cart_item_id: str, user_id: str) -> Optional[CartItem]:
        """Get a specific cart item belonging to the user."""
        query = select(CartItem).options(
            selectinload(CartItem.product)
        ).where(
            CartItem.cart_item_id == cart_item_id,
            CartItem.user_id == user_id,
            CartItem.is_active == True
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_cart_item(db: AsyncSession, cart_item_id: str, user_id: str, 
                             cart_data: CartItemUpdate) -> Optional[CartItem]:
        """Update cart item quantity."""
        cart_item = await CartService.get_cart_item(db, cart_item_id, user_id)
        if not cart_item:
            return None
        
        cart_item.quantity = cart_data.quantity
        cart_item.updated_at = datetime.datetime.utcnow()
        
        await db.commit()
        await db.refresh(cart_item)
        return cart_item
    
    @staticmethod
    async def remove_cart_item(db: AsyncSession, cart_item_id: str, user_id: str) -> bool:
        """Remove item from cart (soft delete)."""
        cart_item = await CartService.get_cart_item(db, cart_item_id, user_id)
        if not cart_item:
            return False
        
        cart_item.is_active = False
        cart_item.updated_at = datetime.datetime.utcnow()
        
        await db.commit()
        return True
    
    @staticmethod
    async def calculate_cart_summary(cart_items: List[CartItem]) -> dict:
        """Calculate cart summary with totals."""
        total_items = sum(item.quantity for item in cart_items)
        total_amount = sum(item.quantity * item.product.price for item in cart_items)
        
        return {
            "total_items": total_items,
            "total_amount": Decimal(str(total_amount))
        }