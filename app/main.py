from app import models
from app.models import User
from app.database import engine, Base, SessionLocal

Base.metadata.create_all(bind=engine)

db = SessionLocal()

user = User(
    first_name="Simon",
    last_name="Santus",
    email="simon@email.com",
    hashed_password="12345",
)

db.add(user)
db.commit()
db.refresh(user)

print(user.id)

db.close()