from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Database URL (matches alembic.ini)
SQLALCHEMY_DATABASE_URL = "sqlite:///myshop.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()