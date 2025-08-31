from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.base import SchemaBase


class ProductBase(BaseModel):
    product_id: str
    product_name: str
    price: float
    description: str
    image_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    product_name: str
    description: str
    price: float
    image_url: Optional[str] = None
    stock_quantity: int
    category_id: str
    subcategory_id: Optional[str] = None
    is_active: bool = True


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = None
    category_id: Optional[str] = None
    subcategory_id: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    status: str
    data: List[ProductBase]
    
    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(BaseModel):
    category_id: str
    category_name: str
    model_config = ConfigDict(from_attributes=True)


class SubcategoryResponse(BaseModel):
    subcategory_id: str
    subcategory_name: str
    model_config = ConfigDict(from_attributes=True)

