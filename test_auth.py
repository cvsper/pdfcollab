#!/usr/bin/env python3
"""
Test script to verify authentication functionality
"""
import requests
import json

def test_authentication():
    """Test authentication endpoints"""
    base_url = "http://localhost:5006"
    
    print("🧪 Testing PDF Collaborator Authentication System")
    print("=" * 50)
    
    # Test 1: Access protected route without authentication
    print("\n1. Testing protected route access without authentication...")
    try:
        response = requests.get(f"{base_url}/", allow_redirects=False)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Redirects to login as expected")
        else:
            print("   ❌ Should redirect to login")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Access login page
    print("\n2. Testing login page access...")
    try:
        response = requests.get(f"{base_url}/auth/login")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Login page accessible")
            if "Sign In" in response.text:
                print("   ✅ Login form found")
            else:
                print("   ❌ Login form not found")
        else:
            print("   ❌ Login page not accessible")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Access registration page
    print("\n3. Testing registration page access...")
    try:
        response = requests.get(f"{base_url}/auth/register")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Registration page accessible")
            if "Sign up" in response.text or "Create Account" in response.text:
                print("   ✅ Registration form found")
            else:
                print("   ❌ Registration form not found")
        else:
            print("   ❌ Registration page not accessible")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Test Google OAuth endpoint
    print("\n4. Testing Google OAuth initialization...")
    try:
        response = requests.get(f"{base_url}/auth/google", allow_redirects=False)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            if 'google' in redirect_url.lower():
                print("   ✅ Google OAuth redirect works")
            else:
                print(f"   ⚠️  Redirects to: {redirect_url}")
        else:
            print("   ❌ OAuth endpoint not working")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Authentication system tests completed!")
    print("\n📋 Next steps:")
    print("   1. Visit http://localhost:5006 to test the full flow")
    print("   2. Try registering a new user")
    print("   3. Test login/logout functionality")
    print("   4. Set up Google OAuth credentials if needed")

if __name__ == "__main__":
    test_authentication()