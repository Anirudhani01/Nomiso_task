#!/usr/bin/env python3
try:
    print("Testing imports...")
    
    print("1. Testing config...")
    from config import DATABASE_URL
    print(f"   DATABASE_URL: {DATABASE_URL[:50]}...")
    
    print("2. Testing auth_models...")
    from auth_models import create_tokens, TokenResponse
    print("   auth_models imported successfully")
    
    print("3. Testing main app...")
    from main import app
    print("   main app imported successfully")
    
    print("✅ All imports successful!")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
