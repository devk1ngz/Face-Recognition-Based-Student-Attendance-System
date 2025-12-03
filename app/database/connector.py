import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__)) 
APP_DIR = os.path.dirname(CURRENT_DIR)                   
ROOT_DIR = os.path.dirname(APP_DIR)                      

DATA_DIR = os.path.join(ROOT_DIR, "data")
DB_NAME = "student_management.db"


if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DB_PATH = os.path.join(DATA_DIR, DB_NAME)
DB_URI = f"sqlite:///{DB_PATH}"

print(f"Database Path: {DB_PATH}")


engine = create_engine(DB_URI, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

def get_session():

    return SessionLocal()

def init_db():
    import app.database.models
    
    Base.metadata.create_all(engine)
    print("Đã khởi tạo Database thành công!")