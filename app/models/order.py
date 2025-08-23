import uuid
import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from app.core.database import Base




class Order(Base):
    """
    SQLAlchemy model for the 'orders' table.
    Stores order information.
    """
    __tablename__ = 'orders'

    order_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.user_id'))
    address_id = Column(String, ForeignKey('addresses.address_id')) # Link to delivery address
    total_amount = Column(Numeric(10, 2))
    order_status = Column(String(28)) # e.g., 'Pending', 'Processing', 'Delivered'
    payment_status = Column(String(28)) # e.g., 'Pending', 'Paid', 'Failed'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships: one-to-many (Order -> OrderItem), many-to-one (Order -> User, Order -> Address)
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    address = relationship("Address")

class OrderItem(Base):
    """
    SQLAlchemy model for the 'order_items' table.
    Stores individual products within an order.
    """
    __tablename__ = 'order_items'

    order_item_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey('orders.order_id'))
    product_id = Column(String, ForeignKey('products.product_id'))
    quantity = Column(Integer)
    price_at_purchase = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships: many-to-one (OrderItem -> Order, OrderItem -> Product)
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
