from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    tasks = relationship("Tasks", back_populates="user")


class Tasks(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    context = Column(String, index=True)
    status = Column(Boolean, default=False, index=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))

    user = relationship("User", back_populates="tasks")
