import uuid
import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from app.core.database import Base



class Offer(Base):
    """
    SQLAlchemy model for the 'offers' table.
    Stores promotion details.
    """
    __tablename__ = 'offers'
    
    offer_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    offer_name = Column(String(50))
    discount_type = Column(String(20)) # e.g., 'percentage' or 'fixed'
    discount_value = Column(Numeric(5, 2))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    
    # Foreign keys to link the offer to a specific product or subcategory
    product_id = Column(String, ForeignKey('products.product_id'), nullable=True)
    subcategory_id = Column(String, ForeignKey('subcategories.subcategory_id'), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships (optional, for clarity)
    product = relationship("Product")
    subcategory = relationship("Subcategory")
