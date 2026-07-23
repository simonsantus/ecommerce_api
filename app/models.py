from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean

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