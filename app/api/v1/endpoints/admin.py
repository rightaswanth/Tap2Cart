from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, func, select
from app.core.database import get_db
from app.core.dependencies import get_current_admin_user, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order
from app.models.product import Product
from app.services.admin import AdminService

router = APIRouter(tags=["admin"])

@router.get("/dashboard", summary="Get dashboard statistics")
async def get_dashboard(
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive dashboard statistics for admin interface."""
    stats = await AdminService.get_dashboard_stats(db)
    return stats

@router.get("/activity", summary="Get recent activity")
async def get_recent_activity(
    limit: int = 20,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recent system activity for admin dashboard."""
    activity = await AdminService.get_recent_activity(db, limit)
    return activity

@router.get("/users", summary="Get users summary")
async def get_users_summary(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get users summary with order statistics."""
    users = await AdminService.get_users_summary(db, skip, limit)
    return users

@router.get("/products", summary="Get products summary")
async def get_products_summary(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get products summary with sales statistics."""
    products = await AdminService.get_products_summary(db, skip, limit)
    return products

@router.get("/orders", summary="Get orders summary")
async def get_orders_summary(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get orders summary for admin interface."""
    orders = await AdminService.get_orders_summary(db, skip, limit)
    return orders

@router.get("/system/health", summary="Get system health")
async def get_system_health(
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get system health information."""
    health = await AdminService.get_system_health(db)
    return health

@router.get("/analytics/revenue", summary="Get revenue analytics")
async def get_revenue_analytics(
    days: int = 30,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get revenue analytics for the specified period."""
    from sqlalchemy import func, text
    from datetime import datetime, timedelta
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Daily revenue for the period
    revenue_query = select(
        func.date(Order.created_at).label('date'),
        func.sum(Order.total_amount).label('revenue')
    ).where(
        Order.payment_status == 'Paid',
        Order.created_at >= start_date,
        Order.created_at <= end_date
    ).group_by(func.date(Order.created_at)).order_by('date')
    
    result = await db.execute(revenue_query)
    
    revenue_data = [
        {"date": str(row.date), "revenue": float(row.revenue)}
        for row in result.all()
    ]
    
    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily_revenue": revenue_data,
        "total_revenue": sum(item["revenue"] for item in revenue_data)
    }

@router.get("/analytics/top-products", summary="Get top selling products")
async def get_top_products(
    limit: int = 10,
    current_user: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get top selling products."""
    from models.order import OrderItem
    
    query = select(
        Product.product_name,
        Product.price,
        func.sum(OrderItem.quantity).label('total_sold'),
        func.sum(OrderItem.quantity * OrderItem.price_at_purchase).label('total_revenue')
    ).join(OrderItem).group_by(
        Product.product_id, Product.product_name, Product.price
    ).order_by(desc('total_sold')).limit(limit)
    
    result = await db.execute(query)
    
    return [
        {
            "product_name": row.product_name,
            "price": float(row.price),
            "total_sold": row.total_sold,
            "total_revenue": float(row.total_revenue)
        }
        for row in result.all()
    ]