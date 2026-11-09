"""
VP Info Solutions Pvt Ltd - Antigravity Lead Management System
Database Configuration & SQLAlchemy Setup
Supports MySQL (Production) and SQLite (Local / Out-of-the-box demo)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Default to SQLite for immediate runability; can be overridden by setting DATABASE_URL
# e.g., DATABASE_URL=mysql+pymysql://root:password@localhost:3306/vp_antigravity
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./antigravity.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
