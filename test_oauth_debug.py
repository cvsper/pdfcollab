#!/usr/bin/env python3
"""
Debug script to test OAuth configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_oauth_config():
    """Test OAuth configuration"""
    print("🔍 OAuth Configuration Debug")
    print("=" * 40)
    
    # Check environment variables
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    redirect_uri = os.getenv('OAUTH_REDIRECT_URI')
    
    print(f"GOOGLE_CLIENT_ID: {client_id[:20] + '...' if client_id else 'Not set'}")
    print(f"GOOGLE_CLIENT_SECRET: {client_secret[:10] + '...' if client_secret else 'Not set'}")
    print(f"OAUTH_REDIRECT_URI: {redirect_uri}")
    
    if client_id and client_secret:
        print("\n✅ OAuth credentials are configured")
        
        # Test if we can import and initialize OAuth
        try:
            from authlib.integrations.flask_client import OAuth
            from flask import Flask
            
            app = Flask(__name__)
            app.config['SECRET_KEY'] = 'test'
            app.config['GOOGLE_CLIENT_ID'] = client_id
            app.config['GOOGLE_CLIENT_SECRET'] = client_secret
            
            oauth = OAuth(app)
            google = oauth.register(
                name='google',
                client_id=client_id,
                client_secret=client_secret,
                server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
                client_kwargs={'scope': 'openid email profile'}
            )
            
            print("✅ OAuth client registration successful")
            print(f"✅ Google client registered: {hasattr(oauth, 'google')}")
            
        except Exception as e:
            print(f"❌ OAuth initialization failed: {e}")
    else:
        print("\n❌ OAuth credentials missing")
        
    print("\n" + "=" * 40)
    print("Next: Restart your Flask app to load these credentials")

if __name__ == "__main__":
    test_oauth_config()