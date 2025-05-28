from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Create database file if it doesn't exist
if not os.path.exists("myshop.db"):
    with open("myshop.db", "w") as f:
        pass  # Create empty file

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