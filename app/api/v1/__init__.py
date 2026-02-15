from fastapi import APIRouter

from .endpoints import products
from .endpoints import category
from .endpoints import orders
from .endpoints import cart
from .endpoints import admin
from .endpoints import address
from .endpoints import user_auth


v1_router = APIRouter()

# v1_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])
v1_router.include_router(products.router, prefix="/products", tags=["products"])
v1_router.include_router(category.router, prefix="/category", tags=["category"])
v1_router.include_router(orders.router, prefix="/orders", tags=["orders"])
v1_router.include_router(cart.router, prefix="/cart", tags=["cart"])
v1_router.include_router(admin.router, prefix="/admin", tags=["admin"])
v1_router.include_router(address.router, prefix="/address", tags=["address"])
v1_router.include_router(user_auth.router, prefix="/auth", tags=["auth"])