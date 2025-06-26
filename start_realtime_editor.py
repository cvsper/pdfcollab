#!/usr/bin/env python3
"""
Quick start script for the Real-Time PDF Editor
"""

import os
import sys
from flask import Flask

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'flask',
        'flask_socketio', 
        'flask_sqlalchemy',
        'fitz',  # PyMuPDF
        'PIL',   # Pillow
        'psycopg2',
        'dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n📦 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Check if environment is properly configured"""
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print("⚠️  .env file not found")
        print("📝 Create .env file with your database credentials:")
        print("""
# Database Configuration
DB_HOST=your-supabase-host
DB_USER=your-db-user  
DB_PASSWORD=your-db-password
DB_NAME=postgres
DB_PORT=5432

# Supabase API (optional)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key
FLASK_DEBUG=true
        """)
        return False
    
    return True

def check_test_pdf():
    """Check if test PDF exists"""
    if not os.path.exists('homeworks.pdf'):
        print("📄 Test PDF 'homeworks.pdf' not found")
        print("   You can still upload PDFs through the web interface")
        return False
    return True

def main():
    """Main startup function"""
    print("🚀 STARTING REAL-TIME PDF EDITOR")
    print("=" * 50)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies installed")
    
    # Check environment
    print("⚙️  Checking environment...")
    env_ready = check_environment()
    if not env_ready:
        print("⚠️  Environment not fully configured, but will try to start anyway")
    else:
        print("✅ Environment configured")
    
    # Check test PDF
    print("📄 Checking for test PDF...")
    pdf_exists = check_test_pdf()
    if pdf_exists:
        print("✅ Test PDF found")
    
    print("\n🎯 STARTING APPLICATION...")
    print("-" * 30)
    
    try:
        # Import and run the app
        from app import app, socketio
        
        print("✅ Application loaded successfully")
        print("🌐 Starting server...")
        print("\n📱 ACCESS POINTS:")
        print("   Main App:      http://localhost:5006")
        print("   Real-time Editor: http://localhost:5006/realtime-editor")
        print("   Dashboard:     http://localhost:5006/dashboard")
        print("\n💡 FEATURES:")
        print("   ⚡ Real-time collaborative editing")
        print("   📄 PDF field detection and positioning")
        print("   👥 Multi-user synchronization") 
        print("   💾 Database persistence")
        print("   📥 Force-visible PDF generation")
        print("\n🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Start the server with SocketIO
        socketio.run(app, 
                    debug=True, 
                    port=5006, 
                    host='0.0.0.0',
                    allow_unsafe_werkzeug=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("🔧 Make sure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()