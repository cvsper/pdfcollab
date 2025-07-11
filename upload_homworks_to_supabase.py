#!/usr/bin/env python3
"""
Upload homworks.pdf to Supabase Storage for deployment
"""

import os
from supabase_api import get_supabase_api
from config import Config

def upload_homworks_to_supabase():
    """Upload homworks.pdf to Supabase Storage"""
    
    print("📤 Uploading homworks.pdf to Supabase Storage")
    print("=" * 50)
    
    # Check if local file exists
    homworks_path = os.path.join(os.path.dirname(__file__), 'homworks.pdf')
    
    if not os.path.exists(homworks_path):
        print(f"❌ Error: {homworks_path} not found")
        return False
    
    file_size = os.path.getsize(homworks_path)
    print(f"✅ Found local file: {homworks_path}")
    print(f"📊 File size: {file_size:,} bytes")
    
    # Get Supabase API client
    supabase_api = get_supabase_api()
    
    if not supabase_api.is_available():
        print("❌ Supabase API not available")
        print("   Check your SUPABASE_URL and SUPABASE_ANON_KEY in environment variables")
        return False
    
    print("✅ Supabase API client available")
    
    # Test connection first
    if not supabase_api.test_connection():
        print("❌ Supabase connection test failed")
        return False
    
    # Upload the file
    try:
        print("🌐 Uploading homworks.pdf to Supabase Storage...")
        
        # Upload to 'pdfs' bucket
        public_url = supabase_api.upload_pdf(homworks_path, bucket_name='pdfs')
        
        if public_url:
            print(f"🎉 SUCCESS! homworks.pdf uploaded to Supabase")
            print(f"📁 Public URL: {public_url}")
            print()
            print("✅ Your app will now load homworks.pdf from Supabase on Render!")
            print("✅ No need to include the PDF file in your deployment")
            
            # Test download to verify
            print("\n🔍 Testing download...")
            test_data = supabase_api.download_pdf('homworks.pdf', 'pdfs')
            if test_data and len(test_data) == file_size:
                print("✅ Download test successful - file integrity verified")
            else:
                print("⚠️  Download test failed or file size mismatch")
            
            return True
        else:
            print("❌ Upload failed - no public URL returned")
            return False
            
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def verify_supabase_setup():
    """Verify Supabase configuration"""
    print("🔧 Verifying Supabase Configuration")
    print("=" * 40)
    
    if Config.SUPABASE_URL:
        print(f"✅ SUPABASE_URL: {Config.SUPABASE_URL[:50]}...")
    else:
        print("❌ SUPABASE_URL not configured")
    
    if Config.SUPABASE_ANON_KEY:
        print(f"✅ SUPABASE_ANON_KEY: {Config.SUPABASE_ANON_KEY[:20]}...")
    else:
        print("❌ SUPABASE_ANON_KEY not configured")
    
    print()

def check_storage_bucket():
    """Check if the pdfs bucket exists"""
    print("🪣 Checking Storage Bucket")
    print("=" * 30)
    
    supabase_api = get_supabase_api()
    
    if not supabase_api.is_available():
        print("❌ Supabase API not available")
        return
    
    try:
        # Try to list files in the bucket
        response = supabase_api.supabase.storage.from_('pdfs').list()
        print(f"✅ 'pdfs' bucket exists and is accessible")
        print(f"📁 Current files in bucket: {len(response) if response else 0}")
        
        if response:
            for file_info in response[:5]:  # Show first 5 files
                print(f"   - {file_info.get('name', 'unknown')}")
    
    except Exception as e:
        print(f"⚠️  Bucket check failed: {e}")
        print("   You may need to create a 'pdfs' bucket in Supabase Storage")
        print("   Or check your bucket permissions")

def main():
    """Main function"""
    print("🏠 PDF Collaborator - Supabase Upload Tool")
    print("Uploading Connecticut Home Energy Solutions Form")
    print()
    
    # Step 1: Verify configuration
    verify_supabase_setup()
    
    # Step 2: Check bucket
    check_storage_bucket()
    
    # Step 3: Upload file
    success = upload_homworks_to_supabase()
    
    if success:
        print(f"\n🎉 UPLOAD COMPLETE!")
        print(f"📋 Next steps:")
        print(f"   1. Deploy your app to Render")
        print(f"   2. The app will automatically load homworks.pdf from Supabase")
        print(f"   3. No need to include the PDF file in your deployment")
        print(f"\n🔧 How it works:")
        print(f"   • App first tries to download homworks.pdf from Supabase")
        print(f"   • Falls back to local file if Supabase unavailable")
        print(f"   • Perfect for cloud deployment!")
    else:
        print(f"\n❌ UPLOAD FAILED")
        print(f"📋 Troubleshooting:")
        print(f"   1. Check your Supabase credentials in .env")
        print(f"   2. Make sure 'pdfs' bucket exists in Supabase Storage")
        print(f"   3. Check bucket permissions (allow authenticated uploads)")
        print(f"   4. Verify your Supabase project is active")

if __name__ == "__main__":
    main()