#!/usr/bin/env python3
import requests
import json
import os
from pathlib import Path

def test_image_endpoints():
    """Test the new image upload endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 Testing image endpoints...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Server health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return
    
    # Test 2: Login to get token
    login_data = {
        "name": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 3: Get first employee
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{base_url}/employees/", headers=headers)
        if response.status_code == 200:
            employees = response.json()
            if employees:
                first_employee = employees[0]
                emp_id = first_employee["emp_id"]
                print(f"✅ Found employee: {first_employee['Name']} (ID: {emp_id})")
                print(f"   Current image_path: {first_employee.get('image_path')}")
                print(f"   Current image_hash: {first_employee.get('image_hash')}")
            else:
                print("❌ No employees found")
                return
        else:
            print(f"❌ Get employees failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Get employees error: {e}")
        return
    
    # Test 4: Check image endpoint
    try:
        response = requests.get(f"{base_url}/employees/{emp_id}/image", headers=headers)
        if response.status_code == 404:
            print("✅ Image endpoint working (no image exists yet)")
        else:
            print(f"⚠️  Unexpected image response: {response.status_code}")
    except Exception as e:
        print(f"❌ Image endpoint error: {e}")
    
    print("🎯 Image endpoints test completed!")
    print("\n📋 Available image endpoints:")
    print(f"   POST /employees/{{emp_id}}/image - Upload image")
    print(f"   GET /employees/{{emp_id}}/image - Get image info")
    print(f"   DELETE /employees/{{emp_id}}/image - Delete image")
    print(f"   PUT /employees/{{emp_id}}/image - Update image")
    print(f"   Static files: /uploads/{{emp_id}}.png")

if __name__ == "__main__":
    test_image_endpoints()
