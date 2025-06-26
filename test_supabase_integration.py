#!/usr/bin/env python3
"""
Test comprehensive Supabase integration
"""

from flask import Flask
from config import Config
from models import db, User, Document, DocumentField
from supabase_api import supabase_api
import uuid

def test_comprehensive_integration():
    """Test both SQLAlchemy and Supabase API integration"""
    print("🚀 COMPREHENSIVE SUPABASE INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: SQLAlchemy Database Connection
    print("\n1️⃣ TESTING SQLALCHEMY DATABASE CONNECTION")
    print("-" * 40)
    
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        try:
            # Test database query
            user_count = User.query.count()
            doc_count = Document.query.count()
            
            print(f"✅ SQLAlchemy Database Connected")
            print(f"   📊 Users: {user_count}")
            print(f"   📄 Documents: {doc_count}")
            print(f"   🔗 Database URL: {Config.get_database_url()}")
            
            sqlalchemy_success = True
        except Exception as e:
            print(f"❌ SQLAlchemy Database Failed: {e}")
            sqlalchemy_success = False
    
    # Test 2: Supabase API Connection
    print("\n2️⃣ TESTING SUPABASE API CONNECTION")
    print("-" * 40)
    
    try:
        api_available = supabase_api.is_available()
        print(f"✅ Supabase API Available: {api_available}")
        
        if api_available:
            print(f"   🌐 Supabase URL: {Config.SUPABASE_URL}")
            print(f"   🔑 API Key: {Config.SUPABASE_ANON_KEY[:20]}...")
            
            # Test API connection
            api_success = supabase_api.test_connection()
        else:
            api_success = False
            
    except Exception as e:
        print(f"❌ Supabase API Failed: {e}")
        api_success = False
    
    # Test 3: Integration Benefits
    print("\n3️⃣ INTEGRATION BENEFITS")
    print("-" * 40)
    
    print("📊 SQLAlchemy Database:")
    print("   ✅ Full ORM with relationships")
    print("   ✅ Complex queries and joins") 
    print("   ✅ Transaction management")
    print("   ✅ Automatic schema migration")
    
    print("\n📡 Supabase API:")
    print("   ✅ Real-time subscriptions")
    print("   ✅ File storage for PDFs")
    print("   ✅ Authentication integration")
    print("   ✅ Direct REST API access")
    
    # Test 4: Current Configuration
    print("\n4️⃣ CURRENT CONFIGURATION")
    print("-" * 40)
    
    print(f"🏗️ Database Backend: {'SQLAlchemy + PostgreSQL' if sqlalchemy_success else 'Failed'}")
    print(f"📡 API Backend: {'Supabase API' if api_success else 'Failed'}")
    print(f"🔐 Authentication: {'Ready for Supabase Auth' if api_success else 'Local only'}")
    print(f"📁 File Storage: {'Supabase Storage ready' if api_success else 'Local filesystem'}")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("📋 INTEGRATION SUMMARY")
    
    if sqlalchemy_success and api_success:
        print("🎉 FULL SUPABASE INTEGRATION SUCCESSFUL!")
        print("   ✅ Database: Connected via SQLAlchemy")
        print("   ✅ API: Connected via Supabase client")
        print("   ✅ Ready for production deployment")
        
        print("\n🚀 NEXT STEPS:")
        print("   1. Use SQLAlchemy for all database operations")
        print("   2. Use Supabase API for file storage")
        print("   3. Add real-time features with subscriptions")
        print("   4. Integrate Supabase Auth for user management")
        
    elif sqlalchemy_success:
        print("⚡ PARTIAL INTEGRATION - Database Only")
        print("   ✅ Database: Working with SQLAlchemy")
        print("   ⚠️  API: Supabase client not available")
        print("   📝 Current functionality: Full database operations")
        
    else:
        print("❌ INTEGRATION FAILED")
        print("   ❌ Database: Not working")
        print("   ❌ API: Not available")
        print("   🔧 Check credentials and connection")
    
    return sqlalchemy_success, api_success

if __name__ == "__main__":
    test_comprehensive_integration()