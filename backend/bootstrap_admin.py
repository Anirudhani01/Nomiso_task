#!/usr/bin/env python3
"""
Bootstrap script to create the first admin user.
Run this script once to create the initial admin account.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth_models import Base, Admin, hash_password
from config import DATABASE_URL

def create_initial_admin():
    """Create the first admin user"""
    engine = create_engine(DATABASE_URL)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Check if any admin already exists
        existing_admin = session.query(Admin).first()
        if existing_admin:
            print(f"Admin already exists: {existing_admin.name}")
            return
        
        # Create initial admin
        admin_name = "admin"
        admin_password = "admin123"  # Change this in production!
        
        hashed_password = hash_password(admin_password)
        admin = Admin(name=admin_name, password_hash=hashed_password)
        
        session.add(admin)
        session.commit()
        session.refresh(admin)
        
        print(f"✅ Initial admin created successfully!")
        print(f"   Username: {admin_name}")
        print(f"   Password: {admin_password}")
        print(f"   ID: {admin.id}")
        print("\n⚠️  IMPORTANT: Change the default password after first login!")
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Creating initial admin user...")
    create_initial_admin()
