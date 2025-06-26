#!/usr/bin/env python3
"""
Test Supabase database connection with SQLAlchemy
"""

from flask import Flask
from config import Config
from models import db, User, Document, DocumentField
import os

def test_database_connection():
    """Test the database connection and create tables"""
    print("🔄 Testing Supabase Database Connection...")
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    try:
        # Initialize database
        db.init_app(app)
        
        with app.app_context():
            print(f"📊 Database URL: {Config.get_database_url()}")
            
            # Test connection
            print("🔍 Testing connection...")
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"✅ Connected to PostgreSQL: {version}")
            
            # Create tables
            print("🏗️  Creating tables...")
            db.create_all()
            print("✅ Tables created successfully")
            
            # Test basic operations
            print("🧪 Testing basic operations...")
            
            # Count existing records
            user_count = db.session.query(User).count()
            doc_count = db.session.query(Document).count()
            field_count = db.session.query(DocumentField).count()
            
            print(f"📊 Current data:")
            print(f"   Users: {user_count}")
            print(f"   Documents: {doc_count}")
            print(f"   Fields: {field_count}")
            
            # Test inserting a user if none exist
            if user_count == 0:
                print("👤 Creating test user...")
                test_user = User(
                    username='test_user',
                    email='test@example.com',
                    password_hash='dummy_hash_for_testing',
                    role='admin'
                )
                db.session.add(test_user)
                db.session.commit()
                print("✅ Test user created")
            
            print("🎉 Database connection test successful!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_connection()
    
    if success:
        print("\n✅ SUCCESS: Supabase database is ready to use!")
        print("📋 You can now:")
        print("   - Run your Flask app with database support")
        print("   - Store documents and user data in Supabase")
        print("   - Use full SQL capabilities")
    else:
        print("\n❌ FAILURE: Database connection issues need to be resolved")
        print("🔧 Check your .env file credentials")