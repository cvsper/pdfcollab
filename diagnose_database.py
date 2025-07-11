#!/usr/bin/env python3
"""
Diagnose Supabase database schema issues
"""

from supabase_client import SupabaseClient
from supabase_api import get_supabase_api
from config import Config
import traceback

def diagnose_database():
    """Diagnose database schema and connection issues"""
    
    print("🔍 PDF Collaborator - Database Diagnosis")
    print("=" * 50)
    
    # Check configuration
    print("1. Configuration Check:")
    if Config.SUPABASE_URL:
        print(f"   ✅ SUPABASE_URL: {Config.SUPABASE_URL[:50]}...")
    else:
        print("   ❌ SUPABASE_URL not configured")
        return
    
    if Config.SUPABASE_ANON_KEY:
        print(f"   ✅ SUPABASE_ANON_KEY: {Config.SUPABASE_ANON_KEY[:20]}...")
    else:
        print("   ❌ SUPABASE_ANON_KEY not configured")
        return
    
    print()
    
    # Test API connection
    print("2. API Connection Test:")
    supabase_api = get_supabase_api()
    
    if supabase_api.is_available():
        print("   ✅ Supabase API client initialized")
        
        # Test basic connection
        try:
            # Simple test query
            response = supabase_api.supabase.table('documents').select('id').limit(1).execute()
            print("   ✅ Basic API connection successful")
        except Exception as e:
            print(f"   ❌ API connection failed: {e}")
    else:
        print("   ❌ Supabase API client not available")
        return
    
    print()
    
    # Test schema structure
    print("3. Schema Structure Test:")
    try:
        # Check if documents table exists and what columns it has
        response = supabase_api.supabase.rpc('get_table_columns', {
            'table_name': 'documents'
        }).execute()
        
        if response.data:
            print("   ✅ documents table exists")
            print("   📋 Columns found:")
            for col in response.data:
                print(f"      - {col.get('column_name', 'unknown')}: {col.get('data_type', 'unknown')}")
        else:
            print("   ❌ Could not get table structure")
            
    except Exception as e:
        print(f"   ⚠️  Schema check failed: {e}")
        print("   This is expected if get_table_columns function doesn't exist")
    
    print()
    
    # Test documents table directly
    print("4. Documents Table Test:")
    try:
        # Try to select with created_by column
        response = supabase_api.supabase.table('documents').select('id, name, status, created_by').limit(1).execute()
        print("   ✅ documents table with created_by column accessible")
        
        if response.data:
            print(f"   📊 Found {len(response.data)} documents")
        else:
            print("   📊 No documents found (table is empty)")
            
    except Exception as e:
        print(f"   ❌ Documents table test failed: {e}")
        print("   🔧 This suggests the created_by column is missing")
    
    print()
    
    # Test alternative query without created_by
    print("5. Alternative Query Test:")
    try:
        # Try without created_by column
        response = supabase_api.supabase.table('documents').select('id, name, status').limit(1).execute()
        print("   ✅ documents table accessible without created_by column")
        
        if response.data:
            print(f"   📊 Found {len(response.data)} documents")
            print("   🔧 Schema update needed: add created_by column")
        else:
            print("   📊 Table exists but is empty")
            
    except Exception as e:
        print(f"   ❌ Alternative query failed: {e}")
        print("   🔧 This suggests more fundamental table issues")
    
    print()
    
    # Test client functions
    print("6. Client Functions Test:")
    try:
        from supabase_client import SupabaseClient
        client = SupabaseClient()
        
        # Test get_documents function
        docs = client.get_documents()
        print(f"   ✅ get_documents() returned {len(docs)} documents")
        
    except Exception as e:
        print(f"   ❌ Client function test failed: {e}")
        print("   📋 Full error:")
        traceback.print_exc()
    
    print()
    
    # Recommendations
    print("🔧 RECOMMENDATIONS:")
    print("=" * 20)
    print("1. Run the SQL migration script:")
    print("   - Open Supabase SQL Editor")
    print("   - Run fix_database_schema.sql")
    print("   - This adds missing columns like created_by")
    print()
    print("2. Check table permissions:")
    print("   - Ensure RLS policies allow anonymous access")
    print("   - Or configure proper authentication")
    print()
    print("3. Verify data:")
    print("   - Check if documents table has data")
    print("   - Verify column types match expectations")

def main():
    """Main function"""
    try:
        diagnose_database()
    except Exception as e:
        print(f"❌ Diagnosis failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()