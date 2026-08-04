from sqlalchemy import create_engine
DATABASE_URL = "sqlite:///eshop.db"
engine = create_engine(DATABASE_URL)

from sqlalchemy.orm import sessionmaker, declarative_base
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()