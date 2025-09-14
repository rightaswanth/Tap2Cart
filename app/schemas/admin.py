from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

class DashboardStats(BaseModel):
    total_users: int
    total_products: int
    total_orders: int
    total_categories: int
    total_revenue: Decimal
    pending_orders: int
    low_stock_products: int

class RecentActivity(BaseModel):
    activity_type: str  # "order", "user_registration", "product_added", etc.
    description: str
    timestamp: datetime
    user_id: Optional[str] = None
    related_id: Optional[str] = None

class UserSummary(BaseModel):
    user_id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    total_orders: int
    total_spent: Decimal
    
    class Config:
        from_attributes = True

class ProductSummary(BaseModel):
    product_id: str
    product_name: str
    price: Decimal
    stock_quantity: Optional[int] = None
    is_active: bool
    category_name: Optional[str] = None
    total_sold: int
    
    class Config:
        from_attributes = True

class OrderSummary(BaseModel):
    order_id: str
    user_email: str
    total_amount: Decimal
    order_status: str
    payment_status: str
    created_at: datetime
    items_count: int
    
    class Config:
        from_attributes = True

class SystemHealth(BaseModel):
    database_status: str
    total_tables: int
    active_sessions: int
    memory_usage: str
    uptime: str