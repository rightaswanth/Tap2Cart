from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from app.services.s3 import S3Service
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Union

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.product import Category, Product, Subcategory
from app.schemas.products import CategoryResponse, ProductBase, ProductCreate, ProductResponse, ProductUpdate, SubcategoryResponse
from app.services.products import ProductService
from app.seeder.product import seed_product_data


router = APIRouter(tags=["products"])


@router.get("/seed-db", summary="Seed the database with sample data")
async def seed_database(db: Session = Depends(get_db)):
    """
    Endpoint to populate the database with some sample data for demonstration.
    """
    return await seed_product_data(db)



@router.get("/", response_model=List[ProductBase], summary="Get a list of products with filtering and pagination")
async def get_products(
    db: Session = Depends(get_db),
    category_id: Optional[str] = Query(None, description="Filter by category ID."),
    subcategory_id: Optional[str] = Query(None, description="Filter by subcategory ID."),
    search: Optional[str] = Query(None, description="Search products by name or description."),
    min_price: Optional[float] = Query(None, description="Filter products with a price greater than or equal to this value."),
    max_price: Optional[float] = Query(None, description="Filter products with a price less than or equal to this value."),
    page: int = Query(1, ge=1, description="Page number for pagination."),
    page_size: int = Query(10, ge=1, le=100, description="Number of products per page."),
):
    """
    Endpoint to retrieve and filter products with extensive query parameters.
    """
    products = await ProductService.get_all_products(
        db=db,
        category=category_id,
        subcategory=subcategory_id,
        search=search,
        min_price=min_price,
        max_price=max_price,
        page=page,
        page_size=page_size
    )
    
    return [
        ProductBase(
            product_id=p.product_id,
            product_name=p.product_name,
            price=float(p.price),
            description=p.description,
            image_url=p.image_url
        ) for p in products
    ]

@router.get("/{product_id}", response_model=ProductBase, summary="Get a single product by ID")
async def get_product(product_id: str, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a single product by its unique ID.
    """
    product = await ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product



@router.post("/", response_model=ProductBase, status_code=201, summary="Create a new product")
async def create_product(
    product_name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock_quantity: int = Form(...),
    category_id: str = Form(...),
    subcategory_id: Optional[str] = Form(None),
    is_active: bool = Form(True),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Endpoint to create a new product with image upload.
    Only accessible to admins.
    """
    # Upload image to S3
    s3_service = S3Service()
    image_url = await s3_service.upload_file(image)
    
    # Create product data object
    product_data = ProductCreate(
        product_name=product_name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        category_id=category_id,
        subcategory_id=subcategory_id,
        is_active=is_active,
        image_url=image_url
    )
    
    return await ProductService.create_product(db, product_data)

@router.put("/{product_id}", response_model=ProductBase, summary="Update an existing product")
async def update_product(product_id: str, product_data: ProductUpdate, db: Session = Depends(get_db)):
    """
    Endpoint to update an existing product.
    """
    updated_product = await ProductService.update_product(db, product_id, product_data)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.delete("/{product_id}", status_code=204, summary="Delete a product")
async def delete_product(product_id: str, db: Session = Depends(get_db)):
    """
    Endpoint to delete a product.
    """
    if not await ProductService.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return
