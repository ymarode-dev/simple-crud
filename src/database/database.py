from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = 'postgresql://postgres:password@localhost:5432/simple-crud'

engine = create_engine(DB_URL)
LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
