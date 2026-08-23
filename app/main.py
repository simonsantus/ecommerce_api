from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from passlib.context import CryptContext

from jose import jwt
from datetime import datetime, timedelta, timezone

from app import models
from app.database import engine, Base, get_db

from app.schemas import (
    CategoryCreate, CategoryResponse, CategoryUpdate, 
    ProductCreate, ProductResponse, ProductUpdate,
    UserCreate, UserResponse, UserLogin,
    CartItemCreate, CartItemResponse, CartResponse, CartItemUpdate,
    OrderCreate, OrderResponse, OrderUpdate, OrderStatus
)

app = FastAPI()

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

SECRET_KEY = "my-super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(

        minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
    ):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authetication credentials"
            )
    
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid authetication credentials"
        )

    user = (
        db.query(models.User)
        .filter(models.User.id == int(user_id))
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
            )
    
    return user

def require_admin(
    current_user: models.User = Depends(get_current_user)
    ):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin acccess required"
            )

    return current_user

def get_or_create_cart(
    current_user: models.User,
    db: Session
    ):
    cart = (
        db.query(models.Cart)
        .filter(models.Cart.user_id == current_user.id)
        .first()
        )
    
    if cart is None:
        cart = models.Cart(
            user_id=current_user.id
        )

        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    return cart


@app.get(
    "/users/me",
    response_model=UserResponse
)
def get_me(
    current_user: models.User = Depends(get_current_user)
    ):
    return current_user

Base.metadata.create_all(bind=engine)

@app.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=201
    )
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
    ):
    new_category = models.Category(
        name=category.name
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category

@app.get(
    "/categories",
    response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    return categories

@app.get(
    "/categories/{category_id}",
    response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)):
    category = (db.query(models.Category)
    .filter(models.Category.id == category_id)
    .first())
    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found")
    return category



@app.patch(
    "/categories/{category_id}",
    response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
    ):
    category = (db.query(models.Category)
    .filter(models.Category.id == category_id)
    .first())
    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found")

    category.name = category_data.name
    db.commit()
    db.refresh(category)
    return category

@app.delete(
    "/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
    ):
    category = (db.query(models.Category)
    .filter(models.Category.id == category_id)
    .first())
    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found")
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}

@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=201
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
    ):
    category = (
        db.query(models.Category)
        .filter(models.Category.id == product.category_id)
        .first()
    )

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )
    
    new_product = models.Product(
        name=product.name,
        brand=product.brand,
        model=product.model,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category_id=product.category_id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

@app.get(
    "/products",
    response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return products

@app.get(
    "/products/{product_id}",
    response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)):

    product = (db.query(models.Product)
    .filter(models.Product.id == product_id)
    .first())

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found")

    return product

@app.patch(
    "/products/{product_id}",
    response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
    ):
    product = (db.query(models.Product)
    .filter(models.Product.id == product_id)
    .first())
    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found")

    update_data = product_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product

@app.delete(
    "/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
    ):
    product = (db.query(models.Product)
    .filter(models.Product.id == product_id)
    .first())

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}

@app.post(
    "/users",
    response_model=UserResponse,
    status_code=201
)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
    ):
    existing_user = (db.query(models.User)
    .filter(models.User.email == user.email)
    .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(user.password)

    new_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
    ):
    user = (
        db.query(models.User)
        .filter(models.User.email == form_data.username)
        .first()
    )    

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    access_token = create_access_token(user.id)

    return {"access_token": access_token, "token_type": "bearer"
    }

@app.get(
    "/cart",
    response_model=CartResponse
    )
def get_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):
    cart = get_or_create_cart(current_user, db)

    return cart

@app.post(
    "/cart/items",
    response_model=CartItemResponse,
    status_code=201
    )
def add_cart_item(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):
    product = (
        db.query(models.Product)
        .filter(models.Product.id == item.product_id)
        .first()
        )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if item.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock"
        )

    cart = get_or_create_cart(
        current_user,
        db
        )
    
    existing_item = (
        db.query(models.CartItem)
        .filter(
            models.CartItem.cart_id == cart.id,
            models.CartItem.product_id == item.product_id
            )
            .first()
            )
    
    if existing_item:
        new_quantity = existing_item.quantity + item.quantity
        if new_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail="Not enough stock"
                )
        
        existing_item.quantity = new_quantity

        db.commit()
        db.refresh(existing_item)

        return existing_item

    new_item = models.CartItem(
        cart_id=cart.id,
        product_id=item.product_id,
        quantity=item.quantity
        )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return new_item

@app.patch(
    "/cart/items/{item_id}",
    response_model=CartItemResponse
)
def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):

    cart = get_or_create_cart(
        current_user,
        db
        )
    
    cart_item = (db.query(
        models.CartItem)
        .filter(
            models.CartItem.id == item_id,
            models.CartItem.cart_id == cart.id)
            .first()
            )

    if cart_item is None:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
            )
    
    product = (
        db.query(models.Product)
        .filter(models.Product.id == cart_item.product_id)
        .first()
        )
    
    if item_data.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock"
            )
    
    cart_item.quantity = item_data.quantity

    db.commit()
    db.refresh(cart_item)

    return cart_item

@app.delete(
    "/cart/items/{item_id}",
    status_code=204
    )
def delete_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):
    cart = get_or_create_cart(
        current_user,
        db
        )

    cart_item = (
        db.query(models.CartItem)
        .filter(
            models.CartItem.id == item_id,
            models.CartItem.cart_id == cart.id
            )
        .first()
        )
    
    if cart_item is None:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
            )

    db.delete(cart_item)
    db.commit()

@app.post(
    "/orders",
    response_model=OrderResponse,
    status_code=201
    )
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):
    
    cart = (
        db.query(models.Cart)
        .filter(models.Cart.user_id == current_user.id)
        .first()
        )

    if cart is None or not cart.cart_items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
            )

    for cart_item in cart.cart_items:
        if cart_item.quantity >cart_item.product.stock:
            raise HTTPException(
                status_code=400,
                detail="Not enough stock for product"
            )

    new_order = models.Order(
        user_id=current_user.id,
        recipient_first_name=order_data.recipient_first_name,
        recipient_last_name=order_data.recipient_last_name,
        recipient_phone=order_data.recipient_phone,
        recipient_email=order_data.recipient_email,
        street=order_data.street,
        city=order_data.city,
        postal_code=order_data.postal_code,
        country=order_data.country,
        payment_method=order_data.payment_method,
        delivery_method=order_data.delivery_method,
        total_price=0
        )

    db.add(new_order)
    db.flush()

    total_price = 0
    for cart_item in cart.cart_items:
        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            unit_price=cart_item.product.price
            )
    
        db.add(order_item)
        cart_item.product.stock -= cart_item.quantity
        total_price += cart_item.product.price * cart_item.quantity
    
    new_order.total_price = total_price

    for cart_item in cart.cart_items:
        db.delete(cart_item)
    
    db.commit()
    db.refresh(new_order)

    return new_order

@app.get(
    "/orders",
    response_model=list[OrderResponse]
    )
def get_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):

    orders = (
            db.query(models.Order)
            .filter(models.Order.user_id == current_user.id)
            .all()
            )

    return orders

@app.get(
    "/orders/{order_id}",
    response_model=OrderResponse
    )
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):

    order = (
            db.query(models.Order)
            .filter(models.Order.id == order_id)
            .first()
            )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
            )

    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to access this order"
            )
    return order

@app.patch(
    "/orders/{order_id}",
    response_model=OrderResponse
)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):

    order = (
        db.query(models.Order)
            .filter(models.Order.id == order_id)
            .first()
                )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
            )

    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed"
            )

    if order.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="Order can no longer be modified"
            )

    update_data = order_data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(order, field, value)

    db.commit()
    db.refresh(order)

    return order
    
@app.patch(
    "/orders/{order_id}/cancel",
    response_model=OrderResponse
    )
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):

    order = (
        db.query(models.Order)
            .filter(models.Order.id == order_id)
            .first()
                )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
            )

    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed"
            )

    if order.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="Order can no longer be modified"
            )

    for order_item in order.order_items:
        order_item.product.stock += order_item.quantity

    order.status = "cancelled"

    db.commit()
    db.refresh(order)

    return order

@app.patch(
    "/admin/orders/{order_id}/status",
    response_model=OrderResponse
    )
def update_order_status(
    order_id: int,
    status_data: OrderStatus,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin)
    ):        

    order = (
        db.query(models.Order)
            .filter(models.Order.id == order_id)
            .first()
                )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not exists"
        )

    allowed_status = ["pending", "shipped", "delivered", "cancelled"]

    if status_data.status not in allowed_status:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status"
            )

    order.status = status_data.status

    db.commit()
    db.refresh(order)

    return order
