import pytest

from fastapi.testclient import TestClient 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, hash_password
from app.database import Base, get_db
from app import models

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread":False})

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind = engine
    )

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture()
def db():

    Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)


    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()

def test_get_products(db):
    response = client.get("/products")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_product(db):
    category = models.Category(
        name="Smartphones"
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = models.Product(
        name="iPhone 16",
        brand="Apple",
        model="16",
        description="Smartphone",
        price=800,
        stock=10,
        category_id=category.id
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    response = client.get(f"/products/{product.id}")

    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_get_product_not_found(db):
    response = client.get("/products/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

def test_create_product_without_auth(db):
    response = client.post(
        "/products",
        json={
            "name": "Test Phone",
            "brand": "Test Brand",
            "model": "T1",
            "description": "Test product",
            "price": 500,
            "stock": 5,
            "category_id": 1
        }
    )

    assert response.status_code == 401

def test_create_product_user(db):
    user = models.User(
        first_name="Test",
        last_name="User",
        email="user@test.com",
        hashed_password=hash_password("password123"),
        is_admin=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    login_response = client.post(
        "/login",
        data={
            "username": "user@test.com",
            "password": "password123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.post(
        "/products",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Test Phone",
            "brand": "Test Brand",
            "model": "T1",
            "description": "Test product",
            "price": 500,
            "stock": 5,
            "category_id": 1
        }
    )

    assert response.status_code == 403

def test_create_product_admin(db):
    admin = models.User(
        first_name="Test",
        last_name="Admin",
        email="admin@test.com",
        hashed_password=hash_password("password123"),
        is_admin=True
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    category = models.Category(
        name="Smartphones"
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    login_response = client.post(
        "/login",
        data={
            "username": "admin@test.com",
            "password": "password123"
        }
    )
    
    token = login_response.json()["access_token"]

    response = client.post(
        "/products",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Test Phone",
            "brand": "Test Brand",
            "model": "T1",
            "description": "Test product",
            "price": 500,
            "stock": 5,
            "category_id": category.id
        }
    )

    assert response.status_code == 201

def test_login_success(db):
    user = models.User(
        first_name="Test",
        last_name="User",
        email="login@test.com",
        hashed_password=hash_password("password123"),
        is_admin=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    response = client.post(
        "/login",
        data={
            "username": "login@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(db):
    user = models.User(
        first_name="Test",
        last_name="User",
        email="login@test.com",
        hashed_password=hash_password("password12345"),
        is_admin=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    response = client.post(
        "/login",
        data={
            "username": "login@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_update_product_admin(db):
    admin = models.User(
        first_name="Test",
        last_name="Admin",
        email="admin@test.com",
        hashed_password=hash_password("password123"),
        is_admin=True
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    category = models.Category(
        name="Smartphones"
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = models.Product(
        name= "Test Phone",
        brand= "Test Brand",
        model= "T1",
        description="Test product",
        price=500,
        stock=5,
        category_id=category.id
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    login_response = client.post(
        "/login",
        data={
            "username": "admin@test.com",
            "password": "password123"
        }
    )
    
    token = login_response.json()["access_token"]

    response = client.patch(
        f"/products/{product.id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "model": "T12"
        }
    )

    assert response.status_code == 200
    assert response.json()["model"] == "T12"

def test_update_product_user(db):
    user = models.User(
        first_name="Test",
        last_name="User",
        email="user@test.com",
        hashed_password=hash_password("password123"),
        is_admin=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    category = models.Category(
        name="Smartphones"
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = models.Product(
        name= "Test Phone",
        brand= "Test Brand",
        model= "T1",
        description="Test product",
        price=500,
        stock=5,
        category_id=category.id
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    login_response = client.post(
        "/login",
        data={
            "username": "user@test.com",
            "password": "password123"
        }
    )
    
    token = login_response.json()["access_token"]

    response = client.patch(
        f"/products/{product.id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "model": "T12"
        }
    )

    assert response.status_code == 403

    db.refresh(product)
    assert product.model == "T1"

def test_update_without_login(db):
    category = models.Category(
        name="Smartphones"
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = models.Product(
        name= "Test Phone",
        brand= "Test Brand",
        model= "T1",
        description="Test product",
        price=500,
        stock=5,
        category_id=category.id
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    response = client.patch(
        f"/products/{product.id}",
        json={
            "model": "T12"
        }
    )

    assert response.status_code == 401

    db.refresh(product)
    assert product.model == "T1"

def test_delete_product_admin(db):
    admin = models.User(
        first_name="Test",
        last_name="Admin",
        email="admin@test.com",
        hashed_password=hash_password("password123"),
        is_admin=True
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    category = models.Category(
        name="Smartphones"
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = models.Product(
        name= "Test Phone",
        brand= "Test Brand",
        model= "T1",
        description="Test product",
        price=500,
        stock=5,
        category_id=category.id
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    login_response = client.post(
        "/login",
        data={
            "username": "admin@test.com",
            "password": "password123"
        }
    )
    
    token = login_response.json()["access_token"]

    response = client.delete(
        f"/products/{product.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    deleted_product = (
        db.query(models.Product)
        .filter(models.Product.id == product.id)
        .first()
    )
    assert deleted_product is None

def test_delete_product_user(db):
    user = models.User(
        first_name="Test",
        last_name="User",
        email="user@test.com",
        hashed_password=hash_password("password123"),
        is_admin=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    category = models.Category(
        name="Smartphones"
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = models.Product(
        name= "Test Phone",
        brand= "Test Brand",
        model= "T1",
        description="Test product",
        price=500,
        stock=5,
        category_id=category.id
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    login_response = client.post(
        "/login",
        data={
            "username": "user@test.com",
            "password": "password123"
        }
    )
    
    token = login_response.json()["access_token"]

    response = client.delete(
        f"/products/{product.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 403

    deleted_product = (
        db.query(models.Product)
        .filter(models.Product.id == product.id)
        .first()
    )
    assert deleted_product is not None

def test_delete_product_without_login(db):
    category = models.Category(
        name="Smartphones"
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    product = models.Product(
        name= "Test Phone",
        brand= "Test Brand",
        model= "T1",
        description="Test product",
        price=500,
        stock=5,
        category_id=category.id
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    response = client.delete(
        f"/products/{product.id}"
    )

    assert response.status_code == 401

    deleted_product = (
        db.query(models.Product)
        .filter(models.Product.id == product.id)
        .first()
    )
    assert deleted_product is not None