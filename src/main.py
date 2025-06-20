from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models import models
from database.database import engine
from auth.auth import get_db, login_user, signup_user
from tasks import tasks
from schema import schemas
from typing import List


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


@app.post("/tasks")
def create_task(task: schemas.TaskData, db: Session = Depends(get_db)):
    return tasks.add_task(task, db)

@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def read_task(task_id: int, db: Session = Depends(get_db)):
    return tasks.get_task(task_id, db)


@app.get("/tasks/user/{user_id}", response_model=List[schemas.TaskOut])
def read_all_tasks(user_id: int, db: Session = Depends(get_db)):
    return tasks.get_all_tasks(user_id, db)


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: schemas.TaskData, db: Session = Depends(get_db)):
    return tasks.update_task(task_id, task, db)

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    return tasks.delete_task(task_id, db)