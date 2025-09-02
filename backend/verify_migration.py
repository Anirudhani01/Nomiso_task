#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import SessionLocal, Employee
from sqlalchemy import inspect

def verify_migration():
    """Verify that image fields were added to the employees table"""
    print("🔍 Verifying database migration...")
    
    db = SessionLocal()
    try:
        # Get table information
        inspector = inspect(db.bind)
        columns = inspector.get_columns('employees')
        
        # Check for new columns
        column_names = [col['name'] for col in columns]
        print(f"📋 All columns in employees table: {column_names}")
        
        # Check specifically for image fields
        if 'image_path' in column_names:
            print("✅ image_path column found")
        else:
            print("❌ image_path column missing")
            
        if 'image_hash' in column_names:
            print("✅ image_hash column found")
        else:
            print("❌ image_hash column missing")
        
        # Test query to make sure everything works
        employee_count = db.query(Employee).count()
        print(f"📊 Total employees: {employee_count}")
        
        # Test that we can access the new fields
        sample_employee = db.query(Employee).first()
        if sample_employee:
            print(f"✅ Sample employee: {sample_employee.Name}")
            print(f"   image_path: {sample_employee.image_path}")
            print(f"   image_hash: {sample_employee.image_hash}")
        
        print("🎯 Migration verification complete!")
        
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_migration()
