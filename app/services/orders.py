import datetime
import uuid
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import and_, desc, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from decimal import Decimal
from typing import List, Optional, Dict
from app.models.user import User
from app.models.order import Order, OrderItem
from app.models.cart import CartItem
from app.models.product import Product
from app.schemas.orders import (
    OrderCreate,
    OrderStatus,
    OrderStatusUpdate,
    OrderUpdate,
    PaymentStatus,
)
from app.services.cart import cart_service

class OrderService:

    async def create_order(
        self,
        db: AsyncSession,
        user_id: Optional[str],
        order_data: OrderCreate
    ) -> Order:

        # 1. Handle Guest/User Creation
        if not user_id:
            if not order_data.phone_number:
                raise ValueError("Phone number required")

            stmt = select(User).where(User.phone_number == order_data.phone_number)
            user = (await db.execute(stmt)).scalar_one_or_none()

            if not user:
                user = User(
                    phone_number=order_data.phone_number,
                    role="user",
                    is_active=True
                )
                db.add(user)
                await db.flush()

            user_id = user.user_id
        
        # 2. Validate Address Ownership (if not guest, or if guest has address linked)
        # For simplicity, we assume address_id is valid FK. 
        # In a real app, we should check `select(Address).where(Address.address_id == order_data.address_id, Address.user_id == user_id)`
        
        product_ids = {item.product_id for item in order_data.items}
        items_map = {item.product_id: item for item in order_data.items}

        # 🔒 Lock products
        stmt = (
            select(Product)
            .where(Product.product_id.in_(product_ids))
            .with_for_update()
        )

        products = (await db.execute(stmt)).scalars().all()

        if len(products) != len(product_ids):
            raise ValueError("Some products not found")

        total_amount = Decimal("0.00")
        order_items = []

        for product in products:
            item_data = items_map[product.product_id]

            # Optional: check stock here
            if product.stock_quantity < item_data.quantity:
                raise ValueError(f"Insufficient stock for {product.product_name}")

            # Ensure price is Decimal
            price = Decimal(str(product.price))
            total = price * Decimal(item_data.quantity)
            total_amount += total

            order_items.append(
                OrderItem(
                    product_id=product.product_id,
                    quantity=item_data.quantity,
                    price_at_purchase=price
                )
            )

        order = Order(
            user_id=user_id,
            address_id=order_data.address_id,
            total_amount=total_amount,
            order_status=OrderStatus.PENDING.value,
            payment_status=PaymentStatus.PENDING.value,
            payment_method=order_data.payment_method,
            tracking_token=str(uuid.uuid4()),
            items=order_items
        )

        db.add(order)

        # Bulk clear cart
        await db.execute(
            delete(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.product_id.in_(product_ids)
            )
        )
        
        await db.commit()
        
        # Re-fetch order with items to ensure they are loaded for response
        stmt = select(Order).options(selectinload(Order.items)).where(Order.order_id == order.order_id)
        result = await db.execute(stmt)
        order = result.scalar_one()

        return order

    async def update_order(
        self,
        db: AsyncSession,
        order_id: str,
        order_data: OrderUpdate,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Optional[Order]:
        order = await self.get(db, order_id, user_id, is_admin)
        if not order:
            return None

        if order.order_status in [OrderStatus.DELIVERED.value, OrderStatus.CANCELLED.value]:
            return None

        update_data = order_data.dict(exclude_unset=True)

        if not is_admin:
            # User can only update address if order is pending
            if order.order_status != OrderStatus.PENDING.value:
                return None
            
            allowed_fields = ['address_id']
            # If user wants to cancel? Usually that's a separate endpoint `cancel_order`.
            # If `order_status` is passed by user, it might be ignored here based on logic below.
            
            update_data = {k: v for k, v in update_data.items() if k in allowed_fields}

        for field, value in update_data.items():
            setattr(order, field, value)

        order.updated_at = datetime.datetime.utcnow()
        await db.commit()
        await db.refresh(order)
        return order

    async def update_order_status(
        self,
        db: AsyncSession,
        order_id: str,
        status_update: OrderStatusUpdate
    ) -> Optional[Order]:
        stmt = select(Order).where(and_(Order.order_id == order_id, Order.is_active == True))
        result = await db.execute(stmt)
        order = result.scalars().first()
        if not order:
            return None
        
        # If Admin cancels order, we must restore stock
        if status_update.order_status == OrderStatus.CANCELLED and order.order_status != OrderStatus.CANCELLED.value:
             success = await self.cancel_order(db, order_id, is_admin=True) # Re-use cancel logic
             if success:
                 # Fetch revised order
                 await db.refresh(order)
                 return order
             else:
                 return None

        order.order_status = status_data.order_status.value
        order.updated_at = datetime.datetime.utcnow()
        await db.commit()
        await db.refresh(order)
        return order

    async def cancel_order(
        self,
        db: AsyncSession,
        order_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> bool:
        # 1. Fetch Order and Items (Implicitly starts transaction if not active)
        query = select(Order).options(
            selectinload(Order.items).selectinload(OrderItem.product)
        ).where(and_(Order.order_id == order_id, Order.is_active == True))

        if not is_admin and user_id:
            query = query.where(Order.user_id == user_id)
        
        # Lock order row
        query = query.with_for_update()

        result = await db.execute(query)
        order = result.scalars().first()

        if not order:
            return False

        if order.order_status in [OrderStatus.DELIVERED.value, OrderStatus.CANCELLED.value]:
            return False

        # 2. Restore Stock
        # We need to lock products to safely increment
        for item in order.items:
             # Reload product with lock to ensure atomic update
             stmt = select(Product).where(Product.product_id == item.product_id).with_for_update()
             res = await db.execute(stmt)
             product = res.scalars().first()
             if product:
                 product.stock_quantity += item.quantity

        # 3. Update Status
        order.order_status = OrderStatus.CANCELLED.value
        order.updated_at = datetime.datetime.utcnow()
        
        await db.commit()
        return True

    async def get_order_status(
        self,
        db: AsyncSession,
        order_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Optional[dict]:
        order = await self.get(db, order_id, user_id, is_admin)
        if not order:
            return None

        return {
            "order_id": order.order_id,
            "order_status": order.order_status,
            "payment_status": order.payment_status,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        }

    async def confirm_order(
        self,
        db: AsyncSession,
        order_id: str,
        transaction_id: Optional[str] = None # Payment gateway transaction ID
    ) -> dict:
        """
        Confirms order payment and deducts stock.
        Concurrency safe: uses FOR UPDATE locking.
        Returns status/message.
        """
        try:
            # 1. Fetch Order
            stmt = select(Order).options(selectinload(Order.items)).where(Order.order_id == order_id)
            result = await db.execute(stmt)
            order = result.scalar_one_or_none()
            
            if not order:
                return {"status": "error", "message": "Order not found"}
            
            if order.payment_status == PaymentStatus.PAID.value:
                 return {"status": "success", "message": "Order already paid"}
            
            # 2. Lock Products & Check Stock
            # Prepare map of product_id -> quantity needed
            items_map = {}
            for item in order.items:
                 if item.product_id in items_map:
                     items_map[item.product_id] += item.quantity
                 else:
                     items_map[item.product_id] = item.quantity
            
            product_stmt = select(Product).where(Product.product_id.in_(items_map.keys())).with_for_update()
            result = await db.execute(product_stmt)
            products = result.scalars().all()
            products_dict = {p.product_id: p for p in products}
            
            if len(products) != len(items_map):
                 # Product disappeared?
                 return {"status": "refund", "message": "Some products unavailable"}
            
            for product in products:
                qty_needed = items_map[product.product_id]
                if product.stock_quantity < qty_needed:
                     # Stock insufficient
                     # In real world: Trigger Refund
                     order.payment_status = PaymentStatus.REFUNDED.value
                     order.order_status = OrderStatus.CANCELLED.value
                     await db.commit()
                     return {"status": "refund", "message": f"Insufficient stock for {product.product_name}. Refund initiated."}
                
                # Deduct Stock
                product.stock_quantity -= qty_needed
            
            # 3. Mark Paid
            order.payment_status = PaymentStatus.PAID.value
            order.order_status = OrderStatus.PROCESSING.value # Or Confirmed
            # order.transaction_id = transaction_id 
            
            await db.commit()
            return {"status": "success", "message": "Order confirmed"}

        except Exception as e:
            await db.rollback()
            print(f"Confirm order error: {e}")
            return {"status": "error", "message": str(e)}

    async def get_by_tracking_token(
        self,
        db: AsyncSession,
        tracking_token: str
    ) -> Optional[Order]:
        stmt = select(Order).options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.address)
        ).where(Order.tracking_token == tracking_token)
        
        result = await db.execute(stmt)
        return result.scalars().first()

order_service = OrderService()
