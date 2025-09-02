#!/usr/bin/env python3
"""
Simple test script to verify backend functionality
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_root():
    """Test the root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_login():
    """Test the login endpoint"""
    print("Testing login endpoint...")
    login_data = {
        "name": "admin",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Login successful! Token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print(f"Login failed: {response.text}")
        return None
    print()

def test_protected_endpoint(token):
    """Test a protected endpoint"""
    if not token:
        print("No token available, skipping protected endpoint test")
        return
    
    print("Testing protected endpoint (/me)...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Protected endpoint successful: {response.json()}")
    else:
        print(f"Protected endpoint failed: {response.text}")
    print()

def test_employees_endpoint(token):
    """Test the employees endpoint"""
    if not token:
        print("No token available, skipping employees endpoint test")
        return
    
    print("Testing employees endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/employees/?skip=0&limit=5", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        employees = response.json()
        print(f"Found {len(employees)} employees")
        if employees:
            print(f"First employee: {employees[0]['Name']}")
    else:
        print(f"Employees endpoint failed: {response.text}")
    print()

if __name__ == "__main__":
    print("🚀 Testing Backend API...")
    print("=" * 50)
    
    try:
        test_root()
        token = test_login()
        test_protected_endpoint(token)
        test_employees_endpoint(token)
        print("✅ All tests completed!")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error during testing: {e}")
