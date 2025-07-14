#!/usr/bin/env python3
"""
Deployment Verification Script
Run this to check if the latest changes are deployed
"""

import requests
import sys

def check_deployment(base_url):
    """Check if deployment has latest changes"""
    
    # Remove trailing slash
    base_url = base_url.rstrip('/')
    
    print(f"🔍 Checking deployment at: {base_url}")
    print("-" * 50)
    
    # Check if the download-support route exists
    test_url = f"{base_url}/download-support/test/test.pdf"
    try:
        response = requests.get(test_url, allow_redirects=False)
        if response.status_code in [302, 404, 401]:
            print("✅ Download support route exists (got expected redirect/error)")
        else:
            print(f"❓ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking route: {e}")
    
    # Check if user2 page loads
    user2_url = f"{base_url}/user2/test-doc-id"
    try:
        response = requests.get(user2_url)
        if response.status_code == 200:
            content = response.text
            
            # Check for signature styling
            if "font-signature" in content:
                print("✅ Signature styling CSS found")
            else:
                print("❌ Signature styling CSS NOT found - deployment may be outdated")
                
            # Check for FormData handling
            if "new FormData(this)" in content:
                print("✅ FormData upload fix found")
            else:
                print("❌ FormData upload fix NOT found - deployment may be outdated")
                
            # Check for supporting files handling
            if "supportingFiles = files;" in content:
                print("✅ File accumulation fix found")
            else:
                print("❌ File accumulation fix NOT found - deployment may be outdated")
                
        else:
            print(f"⚠️  Could not load user2 page: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking user2 page: {e}")
    
    print("-" * 50)
    print("\n📝 If fixes are missing, try:")
    print("1. Clear browser cache (Ctrl+Shift+R)")
    print("2. Check deployment logs")
    print("3. Verify deployment branch is 'mail'")
    print("4. Restart deployment/dyno if needed")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter your deployment URL (e.g., https://yourapp.herokuapp.com): ")
    
    check_deployment(url)