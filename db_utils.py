#!/usr/bin/env python3
"""
Database utility functions for managing Supabase data
"""

from flask import Flask
from config import Config
from models import db, User, Document, DocumentField, AuditLog, DocumentStatus, FieldType
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

def create_app():
    """Create Flask app with database configuration"""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def init_database():
    """Initialize database with tables"""
    app = create_app()
    with app.app_context():
        print("🏗️  Creating database tables...")
        db.create_all()
        print("✅ Database tables created successfully")

def create_test_users():
    """Create test users for development"""
    app = create_app()
    with app.app_context():
        print("👤 Creating test users...")
        
        # Check if users already exist
        if User.query.filter_by(username='user1').first():
            print("⚠️  Test users already exist")
            return
        
        # Create User 1
        user1 = User(
            username='user1',
            email='user1@example.com',
            password_hash=generate_password_hash('password123'),
            role='user'
        )
        db.session.add(user1)
        
        # Create User 2  
        user2 = User(
            username='user2',
            email='user2@example.com',
            password_hash=generate_password_hash('password123'),
            role='user'
        )
        db.session.add(user2)
        
        # Create Admin User
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        
        db.session.commit()
        print("✅ Test users created:")
        print("   - user1 / password123")
        print("   - user2 / password123") 
        print("   - admin / admin123")

def show_database_stats():
    """Show current database statistics"""
    app = create_app()
    with app.app_context():
        print("📊 DATABASE STATISTICS")
        print("=" * 40)
        
        user_count = User.query.count()
        doc_count = Document.query.count()
        field_count = DocumentField.query.count()
        audit_count = AuditLog.query.count()
        
        print(f"👥 Users: {user_count}")
        print(f"📄 Documents: {doc_count}")
        print(f"📝 Fields: {field_count}")
        print(f"📋 Audit Logs: {audit_count}")
        
        if user_count > 0:
            print("\n👤 USERS:")
            users = User.query.all()
            for user in users:
                print(f"   - {user.username} ({user.email}) - {user.role}")
        
        if doc_count > 0:
            print("\n📄 DOCUMENTS:")
            docs = Document.query.all()
            for doc in docs:
                print(f"   - {doc.name} ({doc.status.value}) - {len(doc.fields)} fields")

def clear_test_data():
    """Clear all test data from database"""
    app = create_app()
    with app.app_context():
        print("🗑️  Clearing test data...")
        
        # Delete in reverse order to respect foreign keys
        AuditLog.query.delete()
        DocumentField.query.delete()
        Document.query.delete()
        
        # Only delete test users (keep any real users)
        User.query.filter(User.username.in_(['user1', 'user2', 'test_user'])).delete()
        
        db.session.commit()
        print("✅ Test data cleared")

def create_sample_document():
    """Create a sample document with fields"""
    app = create_app()
    with app.app_context():
        print("📄 Creating sample document...")
        
        # Get or create a user
        user = User.query.filter_by(username='admin').first()
        if not user:
            print("❌ No admin user found. Run create_test_users first.")
            return
        
        # Create sample document
        doc_id = str(uuid.uuid4())
        document = Document(
            id=doc_id,
            name="Sample PDF Document",
            original_filename="sample.pdf",
            file_path="uploads/sample.pdf",
            status=DocumentStatus.DRAFT,
            created_by_id=user.id,
            doc_metadata={
                "source": "test_creation",
                "field_count": 3
            }
        )
        db.session.add(document)
        
        # Create sample fields
        fields = [
            {
                "name": "Full Name",
                "type": FieldType.TEXT,
                "assigned_to": "user1",
                "position": {"x": 100, "y": 200, "width": 200, "height": 30, "page": 0}
            },
            {
                "name": "Email Address", 
                "type": FieldType.EMAIL,
                "assigned_to": "user1",
                "position": {"x": 100, "y": 250, "width": 200, "height": 30, "page": 0}
            },
            {
                "name": "Manager Signature",
                "type": FieldType.SIGNATURE,
                "assigned_to": "user2", 
                "position": {"x": 100, "y": 300, "width": 200, "height": 40, "page": 0}
            }
        ]
        
        for i, field_data in enumerate(fields):
            field = DocumentField(
                id=str(uuid.uuid4()),
                document_id=doc_id,
                name=field_data["name"],
                pdf_field_name=f"field_{i+1}",
                field_type=field_data["type"],
                assigned_to=field_data["assigned_to"],
                position=field_data["position"],
                required=True
            )
            db.session.add(field)
        
        db.session.commit()
        print(f"✅ Sample document created with ID: {doc_id}")

def main():
    """Main CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("📋 Database Utility Commands:")
        print("   python db_utils.py init          - Initialize database")
        print("   python db_utils.py users         - Create test users")
        print("   python db_utils.py stats         - Show database stats")
        print("   python db_utils.py sample        - Create sample document")
        print("   python db_utils.py clear         - Clear test data")
        return
    
    command = sys.argv[1]
    
    if command == "init":
        init_database()
    elif command == "users":
        create_test_users()
    elif command == "stats":
        show_database_stats()
    elif command == "sample":
        create_sample_document()
    elif command == "clear":
        clear_test_data()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()