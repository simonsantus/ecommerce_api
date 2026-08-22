from pydantic import BaseModel, EmailStr

from typing import Optional

from datetime import datetime

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class CategoryCreate(BaseModel):
    name: str

class CategoryResponse(BaseModel):
    id: int
    name: str

class CategoryUpdate(BaseModel):
    name: str

class ProductCreate(BaseModel):
    name: str
    brand: str
    model: str
    description: str
    price: float
    stock: int
    category_id: int

class ProductResponse(BaseModel):
    id: int
    name: str
    brand: str
    model: str
    description: str
    price: float
    stock: int
    is_active: bool
    category_id: int

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int

class CartResponse(BaseModel):
    id: int
    user_id: int
    cart_items: list[CartItemResponse]

class CartItemUpdate(BaseModel):
    quantity: int

class OrderCreate(BaseModel):
    recipient_first_name: str
    recipient_last_name: str
    recipient_phone: str
    recipient_email: EmailStr
    street: str
    city: str
    postal_code: str
    country: str
    payment_method: str
    delivery_method: str

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float

class OrderResponse(BaseModel):
    id: int
    user_id: int
    recipient_first_name: str
    recipient_last_name: str
    recipient_phone: str
    recipient_email: EmailStr
    street: str
    city: str
    postal_code: str
    country: str
    payment_method: str
    delivery_method: str
    created_at: datetime
    status: str
    total_price: float
    order_items: list[OrderItemResponse]

class OrderUpdate(BaseModel):
    recipient_first_name: Optional[str] = None
    recipient_last_name: Optional[str] = None
    recipient_phone: Optional[str] = None
    recipient_email: Optional[EmailStr] = None
    street: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    payment_method: Optional[str] = None
    delivery_method: Optional[str] = None