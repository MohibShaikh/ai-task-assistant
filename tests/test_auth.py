#!/usr/bin/env python3
"""
Test Authentication
Simple script to test user registration and login.
"""

import requests
import json

def test_auth():
    """Test authentication endpoints."""
    base_url = "http://localhost:8080"
    
    print("=== Testing Authentication ===\n")
    
    # Test registration
    print("1. Testing user registration...")
    register_data = {
        "username": "testuser2",
        "email": "test2@example.com", 
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during registration: {e}")
    
    print("\n2. Testing user login...")
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Login successful!")
            result = response.json()
            print(f"User: {result['user']}")
            
            # Get session ID from cookies or response
            session_id = None
            if 'session_id' in result:
                session_id = result['session_id']
            elif 'Set-Cookie' in response.headers:
                # Extract from cookie
                cookies = response.headers['Set-Cookie']
                if 'session_id=' in cookies:
                    session_id = cookies.split('session_id=')[1].split(';')[0]
            
            if session_id:
                print(f"Session ID: {session_id}")
                
                print("\n3. Testing authenticated endpoints...")
                
                # Test getting current user
                headers = {"Authorization": session_id}
                response = requests.get(f"{base_url}/api/auth/me", headers=headers)
                if response.status_code == 200:
                    print("✅ /api/auth/me works!")
                else:
                    print(f"❌ /api/auth/me failed: {response.status_code}")
                
                # Test getting tasks
                response = requests.get(f"{base_url}/api/tasks", headers=headers)
                if response.status_code == 200:
                    print("✅ /api/tasks works!")
                    tasks = response.json()
                    print(f"Found {tasks['total']} tasks")
                else:
                    print(f"❌ /api/tasks failed: {response.status_code}")
                
                # Test getting suggestions
                response = requests.get(f"{base_url}/api/suggestions", headers=headers)
                if response.status_code == 200:
                    print("✅ /api/suggestions works!")
                    suggestions = response.json()
                    print(f"Found {len(suggestions['suggestions'])} suggestions")
                else:
                    print(f"❌ /api/suggestions failed: {response.status_code}")
            else:
                print("❌ Could not extract session ID")
                
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during login: {e}")

if __name__ == "__main__":
    test_auth() 