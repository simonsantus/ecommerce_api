# E-commerce API

A backend REST API for an e-commerce application built with FastAPI and SQLAlchemy.

> Work in progress - the project is actively being developed.

## Current Features

- SQLAlchemy database models
- Relationships between users, products, categories, carts and orders
- Pydantic request and response schemas
- Category CRUD operations
- Database session management
- Input validation and error handling
- User registration and login
- Password hashing with bcrypt
- JWT authentication
- OAuth2password flow
- Current user endpoint
- Admin authorization
- Protected product/category create, update and delete endpoints
- Shopping cart operations

## Planned Features

- Order creation
- Pytest
- Docker

## Technologies

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite
- Uvicorn
- Passlib / bcrypt
- python-jose
- OAuth2 / JWT

## Run the project

Install dependencies:

```bash
pip install -r requirements.txt 
```

Run server:

```bash
uvicorn app.main:app --reload
```

Open API documentation:

```text
http://127.0.0.1:8000/docs
```