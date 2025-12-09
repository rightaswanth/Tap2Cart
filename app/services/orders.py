from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from sqlalchemy.orm import selectinload
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.orders import OrderCreate, OrderStatus, OrderUpdate, OrderStatusUpdate, PaymentStatus
from typing import List, Optional
from decimal import Decimal
import datetime


class OrderService:

    @staticmethod
    async def get_orders(
        db: AsyncSession,
        user_id: Optional[str] = None,
        is_admin: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        query = select(Order).where(Order.is_active == True)
        
        if not is_admin and user_id:
            query = query.where(Order.user_id == user_id)
        elif not is_admin and not user_id:
            return []

        query = query.options(
            selectinload(Order.items).selectinload(OrderItem.product)
        ).order_by(desc(Order.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_order_by_id(
        db: AsyncSession,
        order_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Optional[Order]:
        query = select(Order).options(
            selectinload(Order.items).selectinload(OrderItem.product)
        ).where(and_(Order.order_id == order_id, Order.is_active == True))

        if not is_admin and user_id:
            query = query.where(Order.user_id == user_id)
        elif not is_admin and not user_id:
            return None

        result = await db.execute(query)
        return result.scalars().first()

    @staticmethod
    async def create_order(
        db: AsyncSession,
        user_id: str,
        order_data: OrderCreate
    ) -> Optional[Order]:
        try:
            total_amount = Decimal('0.00')
            
            order = Order(
                user_id=user_id,
                address_id=order_data.address_id,
                total_amount=total_amount,
                order_status=OrderStatus.PENDING.value,
                payment_status=PaymentStatus.PENDING.value
            )

            db.add(order)
            await db.flush()  # assign order_id without committing

            for item_data in order_data.items:
                # Validate product
                stmt = select(Product).where(Product.product_id == item_data.product_id)
                result = await db.execute(stmt)
                product = result.scalars().first()
                if not product or not product.is_active:
                    await db.rollback()
                    return None

                price = item_data.price_at_purchase or product.price
                total_amount += price * item_data.quantity

                order_item = OrderItem(
                    order_id=order.order_id,
                    product_id=item_data.product_id,
                    quantity=item_data.quantity,
                    price_at_purchase=price
                )
                db.add(order_item)

            order.total_amount = total_amount
            order.total_amount = total_amount
            await db.commit()
            
            # Re-fetch the order with eager loading to avoid MissingGreenlet error
            # when accessing relationships in the response model
            stmt = select(Order).options(
                selectinload(Order.items).selectinload(OrderItem.product)
            ).where(Order.order_id == order.order_id)
            
            result = await db.execute(stmt)
            refreshed_order = result.scalars().first()
            
            # Clear cart items for this user
            # We need to find the cart items corresponding to the ordered products
            from app.services.cart import CartService
            
            # Get current user's cart items
            cart_items = await CartService.get_user_cart(db, user_id)
            
            # Create a set of product IDs in the order for fast lookup
            ordered_product_ids = {item.product_id for item in order_data.items}
            
            for cart_item in cart_items:
                if cart_item.product_id in ordered_product_ids:
                    await CartService.remove_cart_item(db, cart_item.cart_item_id, user_id)
            
            return refreshed_order

        except Exception:
            await db.rollback()
            return None

    @staticmethod
    async def update_order(
        db: AsyncSession,
        order_id: str,
        order_data: OrderUpdate,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Optional[Order]:
        order = await OrderService.get_order_by_id(db, order_id, user_id, is_admin)
        if not order:
            return None

        if order.order_status in [OrderStatus.DELIVERED.value, OrderStatus.CANCELLED.value]:
            return None

        update_data = order_data.dict(exclude_unset=True)

        if not is_admin:
            if order.order_status != OrderStatus.PENDING.value:
                return None
            allowed_fields = ['address_id']
            update_data = {k: v for k, v in update_data.items() if k in allowed_fields}

        for field, value in update_data.items():
            setattr(order, field, value)

        order.updated_at = datetime.datetime.utcnow()
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def update_order_status(
        db: AsyncSession,
        order_id: str,
        status_data: OrderStatusUpdate
    ) -> Optional[Order]:
        stmt = select(Order).where(and_(Order.order_id == order_id, Order.is_active == True))
        result = await db.execute(stmt)
        order = result.scalars().first()
        if not order:
            return None

        order.order_status = status_data.order_status.value
        order.updated_at = datetime.datetime.utcnow()
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def cancel_order(
        db: AsyncSession,
        order_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> bool:
        order = await OrderService.get_order_by_id(db, order_id, user_id, is_admin)
        if not order:
            return False

        if order.order_status in [OrderStatus.DELIVERED.value, OrderStatus.CANCELLED.value]:
            return False

        order.order_status = OrderStatus.CANCELLED.value
        order.updated_at = datetime.datetime.utcnow()
        await db.commit()
        return True

    @staticmethod
    async def get_order_status(
        db: AsyncSession,
        order_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Optional[dict]:
        order = await OrderService.get_order_by_id(db, order_id, user_id, is_admin)
        if not order:
            return None

        return {
            "order_id": order.order_id,
            "order_status": order.order_status,
            "payment_status": order.payment_status,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        }
