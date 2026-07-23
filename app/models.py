from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric

from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer,
    primary_key=True)

    first_name = Column(String(100),
    nullable=False)

    last_name = Column(String(100),
    nullable=False)

    email = Column(String(100),
    nullable=False, unique=True)

    hashed_password = Column(String(255),
    nullable=False)    

    created_at = Column(DateTime,
    default=datetime.now, nullable=False)

    role = Column(String(20),
    nullable=False, default="user")

    is_active = Column(Boolean,
    nullable=False, default=True)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer,
    primary_key=True)
    
    name = Column(String(20),
    nullable=False, unique=True)

    products = relationship("Product",
    back_populates="category")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer,
    primary_key=True)

    category_id = Column(Integer,
    ForeignKey("categories.id"),
    nullable=False)

    category = relationship("Category",
    back_populates="products")

    name = Column(String(100),
    nullable=False)

    brand = Column(String(50),
    nullable=False)

    model = Column(String(50),
    nullable=False)

    description = Column(String(1000),
    nullable=False)

    price = Column(Numeric(10, 2),
    nullable=False)

    stock = Column(Integer,
    nullable=False, default=0)

    is_active = Column(Boolean,
    nullable=False, default=True)