import uuid
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ---------- Base Schemas (input) ----------
class CategoryBase(BaseModel):
    category_name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = True
    sort_order: Optional[int] = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    category_name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class SubcategoryBase(BaseModel):
    subcategory_name: str
    category_id: str
    is_active: Optional[bool] = True


class SubcategoryCreate(SubcategoryBase):
    pass


class SubcategoryUpdate(BaseModel):
    subcategory_name: Optional[str] = None
    category_id: Optional[str] = None
    is_active: Optional[bool] = None


# ---------- Response Schemas (output) ----------
class SubcategoryResponse(BaseModel):
    subcategory_id: str
    subcategory_name: str
    category_id: str   
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    product_id: str
    product_name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    stock_quantity: int
    is_active: bool
    category_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    category_id: str
    category_name: str
    description: Optional[str]
    image_url: Optional[str]
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    subcategories: List[SubcategoryResponse] = []   
    products: List[ProductResponse] = []           

    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    product_id: str
    product_name: str
    price: float
    description: Optional[str] = None

    class Config:
        orm_mode = True 
        
