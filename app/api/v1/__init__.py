from fastapi import APIRouter

from .endpoints import products

v1_router = APIRouter()

# v1_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])
v1_router.include_router(products.router, prefix="/products", tags=["products"])