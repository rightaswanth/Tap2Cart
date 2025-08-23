import uuid
import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from app.core.database import Base



class User(Base):
    """
    SQLAlchemy model for the 'users' table.
    Stores user information.
    """
    __tablename__ = 'users'

    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    whatsapp_id = Column(String(28), unique=True, index=True)
    email = Column(String(50))
    phone_number = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships: one-to-many (User -> Addresses, User -> Orders)
    addresses = relationship("Address", back_populates="user")
    orders = relationship("Order", back_populates="user")

class Address(Base):
    """
    SQLAlchemy model for the 'addresses' table.
    Stores a user's delivery addresses.
    """
    __tablename__ = 'addresses'

    address_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.user_id'))
    street_address = Column(String(100))
    city = Column(String(50))
    state = Column(String(50))
    postal_code = Column(String(20))
    country = Column(String(50))
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships: many-to-one (Address -> User)
    user = relationship("User", back_populates="addresses")