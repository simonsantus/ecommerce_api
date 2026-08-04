from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.database import engine, Base, get_db

from app.schemas import CategoryCreate, CategoryResponse, CategoryUpdate

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