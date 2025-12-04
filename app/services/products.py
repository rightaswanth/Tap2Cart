from decimal import Decimal
from typing import List, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Category, Product, Subcategory
from app.schemas.products import ProductCreate, ProductUpdate


class ProductService:
    @staticmethod
    async def get_all_products(
        db: AsyncSession,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        brand: Optional[str] = None,
        rating: Optional[int] = None,  # Not implemented in SQLAlchemy
        page: int = 1,
        page_size: int = 10
    ) -> List[Product]:
        """
        Retrieves and filters products with pagination.
        """
        from sqlalchemy.orm import selectinload
        stmt = select(Product).options(
            selectinload(Product.category),
            selectinload(Product.subcategory)
        ).where(Product.is_active == True)

        if category:
            stmt = stmt.where(Product.category_id == category)
        if subcategory:
            stmt = stmt.where(Product.subcategory_id == subcategory)
        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Product.product_name.ilike(search_pattern),
                    Product.description.ilike(search_pattern)
                )
            )
        if min_price:
            stmt = stmt.where(Product.price >= min_price)
        if max_price:
            stmt = stmt.where(Product.price <= max_price)
        # Note: 'brand' and 'rating' are not supported in your current Product model.

        # Apply pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_product_by_id(db: AsyncSession, product_id: str) -> Optional[Product]:
        """
        Retrieves a single product by its ID.
        """
        stmt = select(Product).where(Product.product_id == product_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    @staticmethod
    async def create_product(db: AsyncSession, product_data: ProductCreate) -> Product:
        """
        Creates a new product in the database.
        """
        new_product = Product(
            product_name=product_data.product_name,
            description=product_data.description,
            price=Decimal(product_data.price),
            image_url=product_data.image_url,
            stock_quantity=product_data.stock_quantity,
            category_id=product_data.category_id,
            subcategory_id=product_data.subcategory_id,
            is_active=product_data.is_active
        )
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        return new_product

    @staticmethod
    async def update_product(db: AsyncSession, product_id: str, product_data: ProductUpdate) -> Optional[Product]:
        """
        Updates an existing product by its ID.
        """
        product = await ProductService.get_product_by_id(db, product_id)
        if not product:
            return None

        update_data = product_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == "price":
                setattr(product, key, Decimal(value))
            else:
                setattr(product, key, value)

        await db.commit()
        await db.refresh(product)
        return product

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: str) -> bool:
        """
        Deletes a product by its ID.
        """
        product = await ProductService.get_product_by_id(db, product_id)
        if not product:
            return False

        await db.delete(product)
        await db.commit()
        return True
