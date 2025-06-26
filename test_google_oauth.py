#!/usr/bin/env python3
"""
Test Google OAuth integration
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_google_oauth():
    """Test Google OAuth endpoints and configuration"""
    print("🔍 Testing Google OAuth Integration")
    print("=" * 50)
    
    # Test 1: Check credentials
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    print(f"✅ Client ID: {client_id[:20] + '...' if client_id else 'Missing'}")
    print(f"✅ Client Secret: {client_secret[:10] + '...' if client_secret else 'Missing'}")
    
    # Test 2: Test Google OAuth endpoints
    print("\n🌐 Testing Google OAuth Endpoints:")
    
    try:
        # Test authorization endpoint
        auth_response = requests.get('https://accounts.google.com/o/oauth2/auth', 
                                   params={'response_type': 'code', 'client_id': 'test'})
        print(f"✅ Authorization endpoint: {auth_response.status_code}")
    except Exception as e:
        print(f"❌ Authorization endpoint error: {e}")
    
    try:
        # Test userinfo endpoint (should return 401 without token)
        userinfo_response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo')
        print(f"✅ UserInfo endpoint: {userinfo_response.status_code} (401 expected)")
    except Exception as e:
        print(f"❌ UserInfo endpoint error: {e}")
    
    # Test 3: Test Flask app OAuth endpoint
    print("\n🚀 Testing Flask App OAuth:")
    
    try:
        app_response = requests.get('http://localhost:5006/auth/google', allow_redirects=False)
        print(f"✅ Flask OAuth endpoint: {app_response.status_code}")
        
        if app_response.status_code == 302:
            redirect_url = app_response.headers.get('Location', '')
            if 'accounts.google.com' in redirect_url:
                print(f"✅ Redirects to Google: {redirect_url[:50]}...")
            else:
                print(f"⚠️  Redirects to: {redirect_url}")
        elif app_response.status_code == 500:
            print("❌ Server error - check Flask app logs")
        
    except Exception as e:
        print(f"❌ Flask app OAuth test failed: {e}")
    
    print("\n" + "=" * 50)
    print("💡 Instructions:")
    print("1. Make sure Flask app is running: python3 app.py")
    print("2. Visit: http://localhost:5006/auth/login")
    print("3. Click 'Continue with Google'")
    print("4. Complete OAuth flow")

if __name__ == "__main__":
    test_google_oauth()