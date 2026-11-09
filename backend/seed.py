"""
VP Info Solutions Pvt Ltd - Lead Management System
Database Seeder - Initializes Admin Account Only
"""

from sqlalchemy.orm import Session
from backend.models import User, UserRole
from backend.auth import hash_password


def seed_database(db: Session):
    # Only seed Admin if no users exist
    if db.query(User).count() > 0:
        return

    print("Seeding initial Admin for VP Info Solutions Pvt Ltd...")

    admin = User(
        username="admin",
        password_hash=hash_password("admin123"),
        full_name="Rajesh Sharma",
        email="rajesh.sharma@vpinfosolutions.com",
        phone="+91 98201 11222",
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    print("Database initialized with Admin account.")
