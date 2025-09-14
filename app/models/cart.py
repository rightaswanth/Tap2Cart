from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey
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

    cart_item_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.user_id'))
    product_id = Column(String, ForeignKey('products.product_id'))
    quantity = Column(Integer, default=1)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="cart_items")  # Assuming User model has cart_items relationship
    product = relationship("Product")
