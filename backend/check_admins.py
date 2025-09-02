#!/usr/bin/env python3
"""
Check what's in the admins table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from auth_models import Base, Admin
from config import DATABASE_URL

def check_admins():
    """Check admins table directly"""
    print("🔍 Checking Admins Table...")
    print(f"Database URL: {DATABASE_URL}")
    print("-" * 50)
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Check tables
    with engine.connect() as connection:
        result = connection.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        print(f"All tables: {tables}")
        
        # Check admins table
        if 'admins' in tables:
            result = connection.execute(text("SELECT * FROM admins"))
            admins = result.fetchall()
            print(f"Admins table has {len(admins)} rows:")
            for admin in admins:
                print(f"  ID: {admin[0]}, Name: {admin[1]}, Hash: {admin[2][:50]}...")
        else:
            print("❌ admins table not found!")
            
        # Check admin table
        if 'admin' in tables:
            result = connection.execute(text("SELECT * FROM admin"))
            admins = result.fetchall()
            print(f"admin table has {len(admins)} rows:")
            for admin in admins:
                print(f"  ID: {admin[0]}, Name: {admin[1]}, Hash: {admin[2][:50]}...")
        else:
            print("❌ admin table not found!")

if __name__ == "__main__":
    check_admins()
