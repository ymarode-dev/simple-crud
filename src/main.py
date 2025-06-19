from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models import models
from database.database import engine
from auth.auth import get_db, login_user, signup_user
from schema import schemas

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def health():
    return {'msg': "FastAPI server is running!"}

@app.post("/auth/login")
def login(data: schemas.LoginData, db: Session = Depends(get_db)):
    return login_user(data, db)

@app.post("/auth/signup")
def signup(data: schemas.SignUpData, db: Session = Depends(get_db)):
    return signup_user(data, db)


