#!/usr/bin/env python3
"""
Simple test to isolate login issue
"""

import requests
import json

def test_login():
    """Test login with detailed error handling"""
    url = "http://localhost:8000/auth/login"
    data = {
        "name": "admin",
        "password": "admin123"
    }
    
    print("Testing login...")
    print(f"URL: {url}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Token: {result.get('access_token', 'No token')[:50]}...")
        else:
            print("Login failed!")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_login()
