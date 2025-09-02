#!/usr/bin/env python3
"""
Recreate admin user using FastAPI database connection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth_models import Base, Admin, hash_password
from config import DATABASE_URL

def recreate_admin():
    """Recreate admin user"""
    print("🔄 Recreating Admin User...")
    print(f"Database URL: {DATABASE_URL}")
    print("-" * 50)
    
    # Create engine (same as FastAPI app)
    engine = create_engine(DATABASE_URL)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created/updated!")
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Delete existing admin users
        session.query(Admin).delete()
        session.commit()
        print("✅ Cleared existing admin users")
        
        # Create new admin user
        admin_password = "admin123"
        hashed_password = hash_password(admin_password)
        admin = Admin(name="admin", password_hash=hashed_password)
        
        session.add(admin)
        session.commit()
        session.refresh(admin)
        
        print(f"✅ Admin user created successfully!")
        print(f"   ID: {admin.id}")
        print(f"   Name: {admin.name}")
        print(f"   Password: {admin_password}")
        
        # Verify
        admin_count = session.query(Admin).count()
        print(f"   Total admin users: {admin_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    recreate_admin()
