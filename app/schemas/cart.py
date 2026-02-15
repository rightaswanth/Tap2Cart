from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class CartItemBase(BaseModel):
    product_id: str
    quantity: int = Field(gt=0, le=100, description="Quantity must be between 1 and 100")

class CartItemAdd(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0, le=100, description="Quantity must be between 1 and 100")

class ProductInfo(BaseModel):
    product_id: str
    product_name: str
    price: Decimal
    image_url: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True

class CartItemResponse(BaseModel):
    cart_item_id: str
    user_id: Optional[str] = None
    guest_id: Optional[str] = None
    product_id: str
    quantity: int
    added_at: datetime
    updated_at: datetime
    product: ProductInfo
    subtotal: Decimal
    
    class Config:
        from_attributes = True

class CartSummary(BaseModel):
    items: List[CartItemResponse]
    total_items: int
    total_amount: Decimal