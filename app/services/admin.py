from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, text
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.product import Category
from app.schemas.admin import (
    DashboardStats, UserSummary, ProductSummary, OrderSummary, 
    RecentActivity, SystemHealth
)
from typing import List, Optional
from decimal import Decimal
import datetime
import psutil
import time
from app.core.security import verify_password, create_access_token
from app.core.redis import redis_client

class AdminService:

    @staticmethod
    async def authenticate_admin(db: AsyncSession, username: str, password: str) -> Optional[str]:
        """Authenticate admin and return access token."""
        result = await db.execute(select(User).where(User.username == username, User.role == 'admin'))
        user = result.scalar_one_or_none()
        
        if not user or not user.password_hash:
            return None
            
        if not verify_password(password, user.password_hash):
            return None
            
        # Create access token
        access_token = create_access_token(subject=user.user_id)
        return access_token

    @staticmethod
    async def logout_admin(token: str) -> bool:
        """Logout admin by blacklisting the token."""
        # Set expiry to match token expiry (default 30 mins = 1800 seconds)
        # In a real app, you'd extract exp from token, but for now we'll use a safe default
        await redis_client.setex(f"blacklist:{token}", 3600, "true")
        return True
    
    @staticmethod
    async def get_dashboard_stats(db: AsyncSession) -> DashboardStats:
        """Get comprehensive dashboard statistics."""
        
        # Total users
        users_query = select(func.count(User.user_id)).where(
            User.is_active == True,
            User.role == 'user'
        )
        users_result = await db.execute(users_query)
        total_users = users_result.scalar() or 0
        
        # Total products
        products_query = select(func.count(Product.product_id)).where(Product.is_active == True)
        products_result = await db.execute(products_query)
        total_products = products_result.scalar() or 0
        
        # Total orders
        orders_query = select(func.count(Order.order_id)).where(Order.is_active == True)
        orders_result = await db.execute(orders_query)
        total_orders = orders_result.scalar() or 0
        
        # Total categories
        categories_query = select(func.count(Category.category_id)).where(Category.is_active == True)
        categories_result = await db.execute(categories_query)
        total_categories = categories_result.scalar() or 0
        
        # Total revenue
        revenue_query = select(func.sum(Order.total_amount)).where(
            Order.is_active == True,
            Order.payment_status == 'Paid'
        )
        revenue_result = await db.execute(revenue_query)
        total_revenue = revenue_result.scalar() or Decimal('0.00')
        
        # Pending orders
        pending_query = select(func.count(Order.order_id)).where(
            Order.is_active == True,
            Order.order_status == 'Pending'
        )
        pending_result = await db.execute(pending_query)
        pending_orders = pending_result.scalar() or 0
        
        # Low stock products (assuming stock_quantity < 10 is low)
        low_stock_query = select(func.count(Product.product_id)).where(
            Product.is_active == True,
            Product.stock_quantity < 10
        )
        low_stock_result = await db.execute(low_stock_query)
        low_stock_products = low_stock_result.scalar() or 0
        
        return DashboardStats(
            total_users=total_users,
            total_products=total_products,
            total_orders=total_orders,
            total_categories=total_categories,
            total_revenue=total_revenue,
            pending_orders=pending_orders,
            low_stock_products=low_stock_products
        )
    
    @staticmethod
    async def get_recent_activity(db: AsyncSession, limit: int = 20) -> List[RecentActivity]:
        """Get recent system activity."""
        activities = []
        
        # Recent orders
        recent_orders_query = select(Order).where(
            Order.is_active == True
        ).order_by(desc(Order.created_at)).limit(10)
        recent_orders_result = await db.execute(recent_orders_query)
        recent_orders = recent_orders_result.scalars().all()
        
        for order in recent_orders:
            activities.append(RecentActivity(
                activity_type="order",
                description=f"New order #{order.order_id[:8]} - ${order.total_amount}",
                timestamp=order.created_at,
                user_id=order.user_id,
                related_id=order.order_id
            ))
        
        # Recent user registrations
        recent_users_query = select(User).where(
            User.is_active == True
        ).order_by(desc(User.created_at)).limit(10)
        recent_users_result = await db.execute(recent_users_query)
        recent_users = recent_users_result.scalars().all()
        
        for user in recent_users:
            activities.append(RecentActivity(
                activity_type="user_registration",
                description=f"New user registered: {user.email}",
                timestamp=user.created_at,
                user_id=user.user_id
            ))
        
        # Sort all activities by timestamp and return limited results
        activities.sort(key=lambda x: x.timestamp, reverse=True)
        return activities[:limit]
    
    @staticmethod
    async def get_users_summary(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[UserSummary]:
        """Get users summary with order statistics."""
        query = select(
            User,
            func.count(Order.order_id).label('total_orders'),
            func.coalesce(func.sum(Order.total_amount), 0).label('total_spent')
        ).outerjoin(Order).where(
            User.is_active == True,
            User.role == 'user'
        ).group_by(User.user_id).order_by(desc('total_spent')).offset(skip).limit(limit)
        
        result = await db.execute(query)
        
        users_summary = []
        for row in result.all():
            user = row.User
            users_summary.append(UserSummary(
                user_id=user.user_id,
                email=user.email,
                full_name=getattr(user, 'full_name', None),
                is_active=user.is_active,
                created_at=user.created_at,
                total_orders=row.total_orders,
                total_spent=Decimal(str(row.total_spent))
            ))
        
        return users_summary
    
    @staticmethod
    async def get_products_summary(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[ProductSummary]:
        """Get products summary with sales statistics."""
        # This assumes you have OrderItem model linked to products
        from models.order import OrderItem
        
        query = select(
            Product,
            Category.category_name,
            func.coalesce(func.sum(OrderItem.quantity), 0).label('total_sold')
        ).outerjoin(Category, Product.category_id == Category.category_id)\
        .outerjoin(OrderItem, Product.product_id == OrderItem.product_id)\
        .where(Product.is_active == True)\
        .group_by(Product.product_id, Category.category_name)\
        .order_by(desc('total_sold'))\
        .offset(skip).limit(limit)
        
        result = await db.execute(query)
        
        products_summary = []
        for row in result.all():
            product = row.Product
            products_summary.append(ProductSummary(
                product_id=product.product_id,
                product_name=product.product_name,
                price=product.price,
                stock_quantity=getattr(product, 'stock_quantity', None),
                is_active=product.is_active,
                category_name=row.category_name,
                total_sold=row.total_sold
            ))
        
        return products_summary
    
    @staticmethod
    async def get_orders_summary(db: AsyncSession, skip: int = 0, limit: int = 50) -> List[OrderSummary]:
        """Get orders summary with user information."""
        query = select(
            Order,
            User.email,
            func.count(OrderItem.order_item_id).label('items_count')
        ).join(User)\
        .outerjoin(OrderItem)\
        .where(Order.is_active == True)\
        .group_by(Order.order_id, User.email)\
        .order_by(desc(Order.created_at))\
        .offset(skip).limit(limit)
        
        result = await db.execute(query)
        
        orders_summary = []
        for row in result.all():
            order = row.Order
            orders_summary.append(OrderSummary(
                order_id=order.order_id,
                user_email=row.email,
                total_amount=order.total_amount,
                order_status=order.order_status,
                payment_status=order.payment_status,
                created_at=order.created_at,
                items_count=row.items_count
            ))
        
        return orders_summary
    
    @staticmethod
    async def get_system_health(db: AsyncSession) -> SystemHealth:
        """Get system health information."""
        
        # Database status check
        try:
            await db.execute(text("SELECT 1"))
            db_status = "Connected"
        except:
            db_status = "Disconnected"
        
        # Get table count
        tables_query = text("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables_result = await db.execute(tables_query)
        total_tables = tables_result.scalar() or 0
        
        # System metrics
        memory = psutil.virtual_memory()
        memory_usage = f"{memory.percent}% ({memory.used // (1024**3)}GB/{memory.total // (1024**3)}GB)"
        
        # Uptime (simplified - you might want to track this differently)
        uptime = "System running"
        
        return SystemHealth(
            database_status=db_status,
            total_tables=total_tables,
            active_sessions=1,  # Simplified - in real app, track active sessions
            memory_usage=memory_usage,
            uptime=uptime
        )
