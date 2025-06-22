#!/usr/bin/env python3
"""
Test script to verify security features are working correctly.
"""

import requests
import json
import time

def test_rate_limiting():
    """Test rate limiting on login endpoint."""
    print("🧪 Testing Rate Limiting...")
    
    base_url = "http://localhost:5000"
    
    # Test multiple rapid login attempts
    for i in range(7):
        try:
            response = requests.post(
                f"{base_url}/api/auth/login",
                json={"username": "test", "password": "test"},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 429:  # Too Many Requests
                print(f"✅ Rate limiting working! Attempt {i+1} blocked with status 429")
                return True
            else:
                print(f"Attempt {i+1}: Status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Server not running. Please start the server first.")
            return False
    
    print("⚠️  Rate limiting may not be working as expected")
    return False

def test_security_headers():
    """Test security headers are present."""
    print("\n🧪 Testing Security Headers...")
    
    try:
        response = requests.get("http://localhost:5000/")
        
        # Check for security headers
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options', 
            'X-XSS-Protection',
            'Content-Security-Policy'
        ]
        
        headers_found = []
        for header in security_headers:
            if header in response.headers:
                headers_found.append(header)
                print(f"✅ {header}: {response.headers[header]}")
            else:
                print(f"❌ {header}: Not found")
        
        if len(headers_found) >= 3:
            print("✅ Security headers are properly configured!")
            return True
        else:
            print("⚠️  Some security headers are missing")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first.")
        return False

def test_input_validation():
    """Test input validation on registration endpoint."""
    print("\n🧪 Testing Input Validation...")
    
    base_url = "http://localhost:5000"
    
    # Test cases
    test_cases = [
        {
            "name": "Short Password",
            "data": {"username": "test", "email": "test@test.com", "password": "123"},
            "expected_status": 400
        },
        {
            "name": "Invalid Email",
            "data": {"username": "test", "email": "invalid-email", "password": "password123"},
            "expected_status": 400
        },
        {
            "name": "Long Username",
            "data": {"username": "a" * 60, "email": "test@test.com", "password": "password123"},
            "expected_status": 400
        }
    ]
    
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{base_url}/api/auth/register",
                json=test_case["data"],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == test_case["expected_status"]:
                print(f"✅ {test_case['name']}: Validation working (Status {response.status_code})")
            else:
                print(f"❌ {test_case['name']}: Expected {test_case['expected_status']}, got {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Server not running. Please start the server first.")
            return False
    
    return True

def main():
    """Run all security tests."""
    print("🔒 SECURITY FEATURES TEST")
    print("=" * 50)
    
    # Wait a moment for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    
    tests = [
        test_security_headers,
        test_rate_limiting,
        test_input_validation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All security tests passed!")
    else:
        print("⚠️  Some security tests failed. Check the implementation.")

if __name__ == "__main__":
    main() 