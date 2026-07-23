from sqlalchemy import create_engine
DATABASE_URL = "sqlite:///eshop.db"
engine = create_engine(DATABASE_URL)

from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(bind=engine)

from sqlalchemy import declarative_base
Base = declarative_base()