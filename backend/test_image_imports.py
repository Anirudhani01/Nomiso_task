#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test all image-related imports"""
    print("🔍 Testing image-related imports...")
    
    try:
        # Test config imports
        from config import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
        print("✅ Config imports successful")
        print(f"   UPLOAD_DIR: {UPLOAD_DIR}")
        print(f"   MAX_FILE_SIZE: {MAX_FILE_SIZE // (1024*1024)}MB")
        print(f"   ALLOWED_EXTENSIONS: {ALLOWED_EXTENSIONS}")
        
        # Test image utils imports
        from image_utils import (
            validate_image_file, compute_image_hash, save_image_with_deduplication,
            get_image_path, delete_employee_image, create_upload_directory
        )
        print("✅ Image utils imports successful")
        
        # Test main app imports
        from main import app, Employee
        print("✅ Main app imports successful")
        
        # Test database model
        from main import SessionLocal
        db = SessionLocal()
        try:
            employee = db.query(Employee).first()
            if employee:
                print(f"✅ Database model test successful - Sample employee: {employee.Name}")
                print(f"   image_path: {employee.image_path}")
                print(f"   image_hash: {employee.image_hash}")
        finally:
            db.close()
        
        print("🎯 All imports and basic functionality tests passed!")
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()
