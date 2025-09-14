from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"
    RETURNED = "Returned"

class PaymentStatus(str, Enum):
    PENDING = "Pending"
    PAID = "Paid"
    FAILED = "Failed"
    REFUNDED = "Refunded"

class OrderItemBase(BaseModel):
    product_id: str
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")
    price_at_purchase: Optional[Decimal] = Field(None, ge=0, decimal_places=2)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    order_item_id: str
    order_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    address_id: str
    
class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(..., min_items=1, description="Order must contain at least one item")

class OrderUpdate(BaseModel):
    address_id: Optional[str] = None
    order_status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None

class OrderStatusUpdate(BaseModel):
    order_status: OrderStatus

class OrderResponse(BaseModel):
    order_id: str
    user_id: str
    address_id: str
    total_amount: Decimal
    order_status: str
    payment_status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True

class OrderSummary(BaseModel):
    order_id: str
    total_amount: Decimal
    order_status: str
    payment_status: str
    created_at: datetime
    items_count: int
    
    class Config:
        from_attributes = True