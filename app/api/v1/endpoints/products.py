from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Union

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.product import Category, Product, Subcategory
from app.schemas.products import CategoryResponse, ProductBase, ProductCreate, ProductResponse, ProductUpdate, SubcategoryResponse
from app.services.products import ProductService


router = APIRouter(tags=["products"])


@router.get("/seed-db", summary="Seed the database with sample data")
def seed_database(db: Session = Depends(get_db)):
    """
    Endpoint to populate the database with some sample data for demonstration.
    """
    # Create sample categories and subcategories
    tech_cat = Category(category_name="Electronics", description="Electronics products.")
    food_cat = Category(category_name="Food & Groceries", description="Food and other groceries.")
    db.add_all([tech_cat, food_cat])
    db.commit()

    tech_subcat = Subcategory(subcategory_name="Computers", category_id=tech_cat.category_id)
    food_subcat = Subcategory(subcategory_name="Produce", category_id=food_cat.category_id)
    db.add_all([tech_subcat, food_subcat])
    db.commit()

    # Create sample products
    product1 = Product(product_name="Laptop", price=1200.50, description="A powerful laptop.", stock_quantity=10, category_id=tech_cat.category_id, subcategory_id=tech_subcat.subcategory_id)
    product2 = Product(product_name="Smartphone", price=750.00, description="A modern smartphone.", stock_quantity=25, category_id=tech_cat.category_id)
    product3 = Product(product_name="Apples", price=2.50, description="Fresh red apples.", stock_quantity=100, category_id=food_cat.category_id, subcategory_id=food_subcat.subcategory_id)
    db.add_all([product1, product2, product3])
    db.commit()
    
    return {"message": "Database seeded successfully!"}


@router.get("/api/products", response_model=List[ProductBase], summary="Get a list of products with filtering and pagination")
def get_products(
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
    products = ProductService.get_all_products(
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

@router.get("/api/products/{product_id}", response_model=ProductBase, summary="Get a single product by ID")
def get_product(product_id: str, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a single product by its unique ID.
    """
    product = ProductService.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/api/products", response_model=ProductBase, status_code=201, summary="Create a new product")
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    """
    Endpoint to create a new product.
    """
    return ProductService.create_product(db, product_data)

@router.put("/api/products/{product_id}", response_model=ProductBase, summary="Update an existing product")
def update_product(product_id: str, product_data: ProductUpdate, db: Session = Depends(get_db)):
    """
    Endpoint to update an existing product.
    """
    updated_product = ProductService.update_product(db, product_id, product_data)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.delete("/api/products/{product_id}", status_code=204, summary="Delete a product")
def delete_product(product_id: str, db: Session = Depends(get_db)):
    """
    Endpoint to delete a product.
    """
    if not ProductService.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return

@router.get("/api/categories", response_model=List[CategoryResponse], summary="Get all product categories")
def get_categories(db: Session = Depends(get_db)):
    """
    Endpoint to get a list of all product categories.
    """
    categories = ProductService.get_all_categories(db)
    return categories

@router.get("/api/subcategories", response_model=List[SubcategoryResponse], summary="Get all product subcategories")
def get_subcategories(db: Session = Depends(get_db)):
    """
    Endpoint to get a list of all product subcategories.
    """
    subcategories = ProductService.get_all_subcategories(db)
    return subcategories
