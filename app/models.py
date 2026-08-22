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

    is_active = Column(Boolean,
    nullable=False, default=True)

    cart = relationship("Cart",
    back_populates="user")

    orders = relationship("Order",
    back_populates="user")

    is_admin = Column(Boolean,
    default=False)

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

    cart_items = relationship("CartItem",
    back_populates="product")

    order_items = relationship("OrderItem",
    back_populates="product")

class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer,
    primary_key=True)

    user_id = Column(Integer,
    ForeignKey("users.id"),
    nullable=False, unique=True)

    user = relationship("User",
    back_populates="cart")

    cart_items = relationship("CartItem",
    back_populates="cart")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer,
    primary_key=True)

    cart_id = Column(Integer,
    ForeignKey("carts.id"),
    nullable=False)

    product_id = Column(Integer,
    ForeignKey("products.id"),
    nullable=False)

    quantity = Column(Integer,
    nullable=False, default=1)

    cart = relationship("Cart",
    back_populates="cart_items")

    product = relationship("Product",
    back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer,
    primary_key=True)

    user_id = Column(Integer,
    ForeignKey("users.id"),
    nullable=False)

    recipient_first_name = Column(String(100),
    nullable=False)

    recipient_last_name = Column(String(100),
    nullable=False)

    recipient_phone = Column(String(100),
    nullable=False)

    recipient_email = Column(String(100),
    nullable=False)

    street = Column(String(100),
    nullable=False)

    city = Column(String(100),
    nullable=False)

    postal_code = Column(String(20),
    nullable=False)

    country = Column(String(100),
    nullable=False)

    payment_method = Column(String(100),
    nullable=False)

    delivery_method = Column(String(100),
    nullable=False)

    created_at = Column(DateTime,
    default=datetime.now, nullable=False)

    status = Column(String(20),
    nullable=False, default="pending")

    total_price = Column(Numeric(10, 2),
    nullable=False)

    user = relationship("User",
    back_populates="orders")

    order_items = relationship("OrderItem",
    back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer,
    primary_key=True)

    order_id = Column(Integer,
    ForeignKey("orders.id"),
    nullable=False)

    product_id = Column(Integer,
    ForeignKey("products.id"),
    nullable=False)

    quantity = Column(Integer,
    nullable=False)

    unit_price = Column(Numeric(10, 2),
    nullable=False)

    order = relationship("Order",
    back_populates="order_items")

    product = relationship("Product",
    back_populates="order_items")