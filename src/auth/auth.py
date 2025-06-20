from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import models
from schema import schemas
from database.database import LocalSession

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def login_user(data: schemas.LoginData, db: Session):
    user = db.query(models.User).filter(models.User.name == data.name).first()
    if user and verify_password(data.password, user.password):
        return {'msg': 'User logged in successfully!'}
    raise HTTPException(status_code=401, detail='Invalid credentials')

def signup_user(data: schemas.SignUpData, db: Session):
    existing_user = db.query(models.User).filter(
        (models.User.name == data.name) | (models.User.email == data.email)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    hashed_pwd = hash_password(data.password)
    new_user = models.User(name=data.name, email=data.email, password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {'msg': 'User created successfully!', 'user_id': new_user.user_id}
