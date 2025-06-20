from sqlalchemy.orm import Session
from models import models
from schema import schemas
from fastapi import HTTPException, status


def validate_user(user_id: int, db: Session):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user


def add_task(data: schemas.TaskData, db: Session):
    validate_user(data.user_id, db)

    existing_task = db.query(models.Tasks).filter(
        (models.Tasks.user_id == data.user_id) & (models.Tasks.title == data.title)
    ).first()

    if existing_task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task with the same title already exists for this user"
        )

    new_task = models.Tasks(
        title=data.title,
        context=data.context,
        user_id=data.user_id,
        status=data.status or False
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"msg": "Task created successfully!", "task_id": new_task.task_id}


def get_task(task_id: int, db: Session):
    task = db.query(models.Tasks).filter(models.Tasks.task_id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


def get_all_tasks(user_id: int, db: Session):
    validate_user(user_id, db)
    tasks = db.query(models.Tasks).filter(models.Tasks.user_id == user_id).all()
    return tasks


def update_task(task_id: int, data: schemas.TaskData, db: Session):
    task = db.query(models.Tasks).filter(models.Tasks.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    validate_user(data.user_id, db)

    task.title = data.title
    task.context = data.context
    task.status = data.status
    db.commit()
    db.refresh(task)
    return {"msg": "Task updated successfully"}


def delete_task(task_id: int, db: Session):
    task = db.query(models.Tasks).filter(models.Tasks.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"msg": "Task deleted successfully"}
