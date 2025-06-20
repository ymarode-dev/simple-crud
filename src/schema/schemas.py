from pydantic import BaseModel, Field
from typing import Optional

class LoginData(BaseModel):
    name: str
    password: str

class SignUpData(BaseModel):
    name: str = Field(..., min_length=4)
    email: str 
    password: str = Field(..., min_length=6)


class TaskData(BaseModel):
    user_id: int
    title: str = Field(..., min_length=1)
    context: str = Field(..., min_length=1)
    status: Optional[bool] = False

class TaskOut(BaseModel):
    task_id: int
    title: str
    context: str
    status: bool
    user_id: int

    class Config:
        from_attributes = True
