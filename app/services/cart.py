
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload
from app.models.cart import CartItem
from app.models.product import Product
from app.schemas.cart import CartItemAdd, CartItemUpdate
from typing import List, Optional, Dict
from decimal import Decimal
import datetime

class CartService:
    def __init__(self):
        self.model = CartItem
    
    async def get_user_cart(    
        self, 
        db: AsyncSession, 
        user_id: Optional[str] = None, 
        guest_id: Optional[str] = None
    ) -> List[CartItem]:
        query = select(CartItem).options(
            selectinload(CartItem.product)
        ).where(CartItem.is_active == True)
        
        if user_id:
            query = query.where(CartItem.user_id == user_id)
        elif guest_id:
            query = query.where(CartItem.guest_id == guest_id)

        query = query.order_by(CartItem.added_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def add_item_to_cart(
        self, 
        db: AsyncSession, 
        user_id: Optional[str], 
        cart_data: CartItemAdd, 
        guest_id: Optional[str] = None
    ) -> Optional[CartItem]:
        
        query = select(CartItem).options(selectinload(CartItem.product)).where(
            CartItem.product_id == cart_data.product_id,
            CartItem.is_active == True
        )
        
        if user_id:
            query = query.where(CartItem.user_id == user_id)
        elif guest_id:
            query = query.where(CartItem.guest_id == guest_id)

        existing_item = (await db.execute(query)).scalar_one_or_none()

        if existing_item:
            existing_item.quantity += cart_data.quantity
            existing_item.updated_at = datetime.datetime.utcnow()
            await db.commit()
            await db.refresh(existing_item)
            return existing_item
            
    
        product = await db.get(Product, cart_data.product_id)
        if not product or not product.is_active:
            return None

        cart_item = CartItem(
            user_id=user_id,
            guest_id=guest_id,
            product_id=cart_data.product_id,
            quantity=cart_data.quantity
        )
        
        db.add(cart_item)
        await db.commit()
        await db.refresh(cart_item)

        cart_item.product = product

        return cart_item
    
    async def get_cart_item(
        self, 
        db: AsyncSession, 
        cart_item_id: str, 
        user_id: Optional[str] = None, 
        guest_id: Optional[str] = None
    ) -> Optional[CartItem]:
        """
        Get a specific cart item belonging to the user or guest.
        """
        query = select(CartItem).options(
            selectinload(CartItem.product)
        ).where(
            CartItem.cart_item_id == cart_item_id,
            CartItem.is_active == True
        )
        
        if user_id:
            query = query.where(CartItem.user_id == user_id)
        elif guest_id:
            query = query.where(CartItem.guest_id == guest_id)
        else:
            return None
            
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_cart_item(
        self, 
        db: AsyncSession, 
        cart_item_id: str, 
        cart_data: CartItemUpdate, 
        user_id: Optional[str] = None, 
        guest_id: Optional[str] = None
    ) -> Optional[CartItem]:
        cart_item = await self.get_cart_item(db, cart_item_id, user_id, guest_id)
        if not cart_item:
            return None
        
        cart_item.quantity = cart_data.quantity
        cart_item.updated_at = datetime.datetime.utcnow()
        
        await db.commit()
        await db.refresh(cart_item)
        return cart_item
    
    async def remove_cart_item(
        self, 
        db: AsyncSession, 
        cart_item_id: str, 
        user_id: Optional[str] = None, 
        guest_id: Optional[str] = None
    ) -> bool:
        cart_item = await self.get_cart_item(db, cart_item_id, user_id, guest_id)
        if not cart_item:
            return False
        
        cart_item.is_active = False
        cart_item.updated_at = datetime.datetime.utcnow()
        
        await db.commit()
        return True
    
    async def calculate_cart_summary(self, cart_items: List[CartItem]) -> dict:
        total_items = sum(item.quantity for item in cart_items)
        total_amount = sum(item.quantity * item.product.price for item in cart_items)
        
        return {
            "total_items": total_items,
            "total_amount": Decimal(str(total_amount))
        }

    async def clear_user_cart_items(
        self, 
        db: AsyncSession, 
        user_id: Optional[str], 
        product_ids: set[str], 
        guest_id: Optional[str] = None
    ) -> None:
        """
        Remove specific items from the user's cart. 
        Intended to be used within a transaction (e.g., during order creation).
        """
        if not product_ids:
            return

        stmt = select(CartItem).where(
            CartItem.product_id.in_(product_ids),
            CartItem.is_active == True
        )
        
        if user_id:
            stmt = stmt.where(CartItem.user_id == user_id)
        elif guest_id:
            stmt = stmt.where(CartItem.guest_id == guest_id)
        else:
            return
        result = await db.execute(stmt)
        cart_items = result.scalars().all()

        for item in cart_items:
            item.is_active = False
            item.updated_at = datetime.datetime.utcnow()
        
        # Note: No commit here, as this is part of a larger transaction

cart_service = CartService()