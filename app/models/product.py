import uuid
import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from app.core.database import Base



class Category(Base):
    """
    SQLAlchemy model for the 'categories' table.
    Stores top-level product categories.
    """
    __tablename__ = 'categories'

    category_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    category_name = Column(String(50))
    description = Column(String(255))
    image_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships: one-to-many (Category -> Subcategory, Category -> Product)
    subcategories = relationship("Subcategory", back_populates="category")
    products = relationship("Product", back_populates="category")

class Subcategory(Base):
    """
    SQLAlchemy model for the 'subcategories' table.
    Stores sub-level product categories.
    """
    __tablename__ = 'subcategories'

    subcategory_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subcategory_name = Column(String(50))
    category_id = Column(String, ForeignKey('categories.category_id'))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships: many-to-one (Subcategory -> Category)
    category = relationship("Category", back_populates="subcategories")
    products = relationship("Product", back_populates="subcategory")

class Product(Base):
    """
    SQLAlchemy model for the 'products' table.
    Stores individual product details.
    """
    __tablename__ = 'products'

    product_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_name = Column(String(100))
    description = Column(String(500))
    price = Column(Numeric(10, 2))
    image_url = Column(String(255))
    stock_quantity = Column(Integer)
    
    # Foreign keys for category and subcategory
    category_id = Column(String, ForeignKey('categories.category_id'))
    subcategory_id = Column(String, ForeignKey('subcategories.subcategory_id'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships: many-to-one (Product -> Category, Product -> Subcategory)
    category = relationship("Category", back_populates="products")
    subcategory = relationship("Subcategory", back_populates="products")
