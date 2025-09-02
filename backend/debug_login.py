#!/usr/bin/env python3
"""
Debug login functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth_models import Admin, Base, get_admin_by_name, verify_password, create_access_token

def debug_login():
    """Debug the login process"""
    from config import DATABASE_URL
    
    print("🔍 Debugging Login Process...")
    print(f"Database URL: {DATABASE_URL}")
    print("-" * 50)
    
    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Test admin lookup
        admin_name = "admin"
        print(f"Looking for admin with name: {admin_name}")
        
        admin = get_admin_by_name(session, admin_name)
        print(f"Admin found: {admin is not None}")
        
        if admin:
            print(f"Admin ID: {admin.id}")
            print(f"Admin name: {admin.name}")
            print(f"Password hash: {admin.password_hash[:50]}...")
            
            # Test password verification
            test_password = "admin123"
            print(f"Testing password: {test_password}")
            
            is_valid = verify_password(test_password, admin.password_hash)
            print(f"Password valid: {is_valid}")
            
            if is_valid:
                # Test token creation
                token = create_access_token(str(admin.id))
                print(f"Token created: {token[:50]}...")
                print("✅ Login process should work!")
            else:
                print("❌ Password verification failed!")
        else:
            print("❌ Admin not found!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    debug_login()
