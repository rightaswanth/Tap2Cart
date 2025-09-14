from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.services.category import CategoryService, SubcategoryService
from app.schemas.category import (
    CategoryResponse, CategoryCreate, CategoryUpdate,
    SubcategoryResponse, SubcategoryCreate, SubcategoryUpdate
)
from app.core.database import get_db  

router = APIRouter(tags=["category"])

# ------------------ Category Endpoints ------------------

@router.get("/", response_model=List[CategoryResponse], summary="Get all categories")
async def get_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    include_inactive: bool = Query(False, description="Include inactive categories"),
    db: AsyncSession = Depends(get_db)   # ✅ Use AsyncSession
):
    categories = await CategoryService.get_all_categories(
        db, skip=skip, limit=limit, include_inactive=include_inactive
    )
    return categories

@router.get("/{category_id}", response_model=CategoryResponse, summary="Get category by ID")
async def get_category(category_id: str, db: AsyncSession = Depends(get_db)):
    category = await CategoryService.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=CategoryResponse, status_code=201, summary="Create a new category")
async def create_category(category_data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    category = await CategoryService.create_category(db, category_data)
    return category

@router.put("/{category_id}", response_model=CategoryResponse, summary="Update a category")
async def update_category(category_id: str, category_data: CategoryUpdate, db: AsyncSession = Depends(get_db)):
    category = await CategoryService.update_category(db, category_id, category_data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.delete("/{category_id}", status_code=204, summary="Delete a category")
async def delete_category(category_id: str, db: AsyncSession = Depends(get_db)):
    if not await CategoryService.delete_category(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return

@router.get("/{category_id}/products", summary="Get products in a category")
async def get_category_products(
    category_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    products = await CategoryService.get_category_products(db, category_id, skip=skip, limit=limit)
    if products is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return products

# ------------------ Subcategory Endpoints ------------------

@router.get("/{category_id}/subcategories", response_model=List[SubcategoryResponse], summary="Get subcategories")
async def get_subcategories(
    category_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    if not await CategoryService.get_category_by_id(db, category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    
    subcategories = await SubcategoryService.get_all_subcategories(   # ✅ added await
        db, category_id=category_id, skip=skip, limit=limit
    )
    return subcategories

@router.post("/{category_id}/subcategories", response_model=SubcategoryResponse, status_code=201, summary="Create subcategory")
async def create_subcategory(category_id: str, subcategory_data: SubcategoryCreate, db: AsyncSession = Depends(get_db)):
    subcategory_data.category_id = category_id
    subcategory = await SubcategoryService.create_subcategory(db, subcategory_data)
    if not subcategory:
        raise HTTPException(status_code=404, detail="Parent category not found")
    return subcategory

@router.get("/subcategories/all", response_model=List[SubcategoryResponse], summary="Get all subcategories")
async def get_all_subcategories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    subcategories = await SubcategoryService.get_all_subcategories(db, skip=skip, limit=limit)
    return subcategories

@router.get("/subcategories/{subcategory_id}", response_model=SubcategoryResponse, summary="Get subcategory by ID")
async def get_subcategory(subcategory_id: str, db: AsyncSession = Depends(get_db)):
    subcategory = await SubcategoryService.get_subcategory_by_id(db, subcategory_id)
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    return subcategory

@router.put("/subcategories/{subcategory_id}", response_model=SubcategoryResponse, summary="Update subcategory")
async def update_subcategory(subcategory_id: str, subcategory_data: SubcategoryUpdate, db: AsyncSession = Depends(get_db)):
    subcategory = await SubcategoryService.update_subcategory(db, subcategory_id, subcategory_data)
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found or invalid parent category")
    return subcategory

@router.delete("/subcategories/{subcategory_id}", status_code=204, summary="Delete subcategory")
async def delete_subcategory(subcategory_id: str, db: AsyncSession = Depends(get_db)):
    if not await SubcategoryService.delete_subcategory(db, subcategory_id):
        raise HTTPException(status_code=404, detail="Subcategory not found")
    return
