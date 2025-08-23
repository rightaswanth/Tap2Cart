from fastapi import APIRouter

from .endpoints import whatsapp, orders

v1_router = APIRouter()

# v1_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])
# v1_router.include_router(orders.router, prefix="/orders", tags=["orders"])