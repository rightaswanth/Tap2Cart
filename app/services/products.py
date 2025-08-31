from decimal import Decimal
from typing import List, Optional
from requests import Session
from sqlalchemy import or_

from app.models.product import Category, Product, Subcategory
from app.schemas.products import ProductCreate, ProductUpdate


class ProductService:
    @staticmethod
    def get_all_products(
        db: Session,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        search: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        brand: Optional[str] = None,
        rating: Optional[int] = None, # Not implemented in SQLAlchemy
        page: int = 1,
        page_size: int = 10
    ) -> List[Product]:
        """
        Retrieves and filters products with pagination.
        """
        query = db.query(Product).filter(Product.is_active == True)
        
        if category:
            query = query.filter(Product.category_id == category)
        if subcategory:
            query = query.filter(Product.subcategory_id == subcategory)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Product.product_name.like(search_pattern),
                    Product.description.like(search_pattern)
                )
            )
        if min_price:
            query = query.filter(Product.price >= min_price)
        if max_price:
            query = query.filter(Product.price <= max_price)
        # Note: 'brand' is not in your provided model, so filtering by it is not supported.
        # Note: 'rating' is not in your provided model, so filtering by it is not supported.

        # Apply pagination
        offset = (page - 1) * page_size
        return query.offset(offset).limit(page_size).all()

    @staticmethod
    def get_product_by_id(db: Session, product_id: str) -> Optional[Product]:
        """
        Retrieves a single product by its ID.
        """
        return db.query(Product).filter(Product.product_id == product_id).first()

    @staticmethod
    def create_product(db: Session, product_data: ProductCreate) -> Product:
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
        db.commit()
        db.refresh(new_product)
        return new_product

    @staticmethod
    def update_product(db: Session, product_id: str, product_data: ProductUpdate) -> Optional[Product]:
        """
        Updates an existing product by its ID.
        """
        product = ProductService.get_product_by_id(db, product_id)
        if not product:
            return None
        
        update_data = product_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if key == 'price':
                setattr(product, key, Decimal(value))
            else:
                setattr(product, key, value)
        
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete_product(db: Session, product_id: str) -> bool:
        """
        Deletes a product by its ID.
        """
        product = ProductService.get_product_by_id(db, product_id)
        if not product:
            return False
        
        db.delete(product)
        db.commit()
        return True

    @staticmethod
    def get_all_categories(db: Session) -> List[Category]:
        """
        Retrieves all categories.
        """
        return db.query(Category).all()

    @staticmethod
    def get_all_subcategories(db: Session) -> List[Subcategory]:
        """
        Retrieves all subcategories.
        """
        return db.query(Subcategory).all()
