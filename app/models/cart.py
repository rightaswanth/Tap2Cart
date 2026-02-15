from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
import datetime

class CartItem(Base):
    """
    SQLAlchemy model for the 'cart_items' table.
    Stores items in user's shopping cart.
    """
    __tablename__ = 'cart_items'
    __table_args__ = (
        Index("ix_cart_user_product", "user_id", "product_id"),
        Index("ix_cart_guest_product", "guest_id", "product_id"),
    )

    cart_item_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.user_id'), nullable=True)
    guest_id = Column(String, nullable=True, index=True)
    product_id = Column(String, ForeignKey('products.product_id'))
    quantity = Column(Integer, default=1)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product")
