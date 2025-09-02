#!/usr/bin/env python3
import requests
import json

# Test the API endpoints
API_BASE = "http://127.0.0.1:8000"

print("🔍 Testing API endpoints...")

# Test 1: Health check
try:
    response = requests.get(f"{API_BASE}/")
    print(f"✅ Health check: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"❌ Health check failed: {e}")

# Test 2: Login
try:
    login_data = {
        "name": "admin",
        "password": "admin123"
    }
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    print(f"✅ Login: {response.status_code}")
    if response.status_code == 200:
        tokens = response.json()
        print(f"   Access token length: {len(tokens.get('access_token', ''))}")
        print(f"   Refresh token length: {len(tokens.get('refresh_token', ''))}")
        print(f"   Expires in: {tokens.get('expires_in')} seconds")
        
        # Test 3: Get employees with token
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        emp_response = requests.get(f"{API_BASE}/employees/?skip=0&limit=5", headers=headers)
        print(f"✅ Get employees: {emp_response.status_code}")
        if emp_response.status_code == 200:
            employees = emp_response.json()
            print(f"   Retrieved {len(employees)} employees")
            if employees:
                print(f"   First employee: {employees[0].get('Name', 'N/A')}")
        else:
            print(f"   Error: {emp_response.text[:200]}")
    else:
        print(f"   Login error: {response.text}")
except Exception as e:
    print(f"❌ Login test failed: {e}")

print("🎯 API test complete!")
