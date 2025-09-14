import uuid
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Category, Subcategory, Product
from app.schemas.category import (
    CategoryCreate, CategoryUpdate,
    SubcategoryCreate, SubcategoryUpdate
)


class CategoryService:

    @staticmethod
    async def get_all_categories(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False
    ) -> List[Category]:
        """
        Retrieves all categories with pagination.
        Eager-loads subcategories to avoid lazy-load IO during serialization.
        """
        stmt = (
            select(Category)
            .options(selectinload(Category.subcategories))  # preload subcategories
        )

        if not include_inactive:
            stmt = stmt.where(Category.is_active == True)

        stmt = stmt.order_by(Category.sort_order, Category.category_name).offset(skip).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().unique().all()

    @staticmethod
    async def get_category_by_id(db: AsyncSession, category_id: str) -> Optional[Category]:
        """
        Retrieves a category by its ID.
        Eager-loads subcategories to avoid lazy-load IO during serialization.
        """
        stmt = (
            select(Category)
            .options(selectinload(Category.subcategories))
            .where(Category.category_id == category_id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def create_category(db: AsyncSession, category_data: CategoryCreate) -> Category:
        """
        Creates a new category.
        """
        category = Category(**category_data.model_dump())
        db.add(category)
        await db.commit()
        await db.refresh(category)

        # Eager-load subcategories (avoid MissingGreenlet error)
        stmt = select(Category).where(Category.category_id == category.category_id)
        result = await db.execute(stmt)
        return result.scalars().first()
    
    @staticmethod
    async def update_category(db: AsyncSession, category_id: str, category_data: CategoryUpdate) -> Optional[Category]:
        """
        Updates an existing category.
        """
        category = await CategoryService.get_category_by_id(db, category_id)
        if not category:
            return None

        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: str) -> bool:
        """
        Deletes a category by its ID.
        """
        category = await CategoryService.get_category_by_id(db, category_id)
        if not category:
            return False

        await db.delete(category)
        await db.commit()
        return True

    @staticmethod
    async def get_category_products(
        db: AsyncSession,
        category_id: str,
        skip: int = 0,
        limit: int = 100
    ):
        """
        Retrieves products in a specific category.
        """
        # We don't need to load the Category relationship here; just ensure the category exists
        category = await CategoryService.get_category_by_id(db, category_id)
        if not category:
            return None

        stmt = (
            select(Product)
            .where(and_(Product.category_id == category_id, Product.is_active == True))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()


class SubcategoryService:

    @staticmethod
    async def get_all_subcategories(
        db: AsyncSession,
        category_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Subcategory]:
        """
        Retrieves all subcategories, optionally filtered by category.
        Eager-load category relationship to avoid lazy fetch when serializing.
        """
        stmt = select(Subcategory).options(selectinload(Subcategory.category)).where(Subcategory.is_active == True)
        if category_id:
            stmt = stmt.where(Subcategory.category_id == category_id)

        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().unique().all()

    @staticmethod
    async def get_subcategory_by_id(db: AsyncSession, subcategory_id: str) -> Optional[Subcategory]:
        """
        Retrieves a subcategory by its ID.
        Eager-load parent category.
        """
        stmt = select(Subcategory).options(selectinload(Subcategory.category)).where(Subcategory.subcategory_id == subcategory_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def create_subcategory(db: AsyncSession, subcategory_data: SubcategoryCreate) -> Optional[Subcategory]:
        """
        Creates a new subcategory.
        """
        # Verify parent category exists
        category = await CategoryService.get_category_by_id(db, subcategory_data.category_id)
        if not category:
            return None

        subcategory = Subcategory(**subcategory_data.model_dump())
        db.add(subcategory)
        await db.commit()
        await db.refresh(subcategory)
        return subcategory

    @staticmethod
    async def update_subcategory(
        db: AsyncSession,
        subcategory_id: str,
        subcategory_data: SubcategoryUpdate
    ) -> Optional[Subcategory]:
        """
        Updates an existing subcategory.
        """
        subcategory = await SubcategoryService.get_subcategory_by_id(db, subcategory_id)
        if not subcategory:
            return None

        update_data = subcategory_data.model_dump(exclude_unset=True)

        # Verify parent category exists if being updated
        if "category_id" in update_data:
            category = await CategoryService.get_category_by_id(db, update_data["category_id"])
            if not category:
                return None

        for field, value in update_data.items():
            setattr(subcategory, field, value)

        await db.commit()
        await db.refresh(subcategory)
        return subcategory

    @staticmethod
    async def delete_subcategory(db: AsyncSession, subcategory_id: str) -> bool:
        """
        Deletes a subcategory by its ID.
        """
        subcategory = await SubcategoryService.get_subcategory_by_id(db, subcategory_id)
        if not subcategory:
            return False

        await db.delete(subcategory)
        await db.commit()
        return True
