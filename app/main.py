from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.database import engine, Base, get_db

from app.schemas import (
    CategoryCreate, 
    CategoryResponse, 
    CategoryUpdate, 
    ProductCreate, 
    ProductResponse, 
    ProductUpdate
)

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.post(
    "/categories",
    response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)):
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
    db: Session = Depends(get_db)):
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
    db: Session = Depends(get_db)):
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
    response_model=ProductResponse
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)):
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
    db: Session = Depends(get_db)):
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
