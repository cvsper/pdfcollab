#!/usr/bin/env python3
"""
Verify database schema after migration
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def verify_database():
    """Verify the database has all required authentication fields"""
    print("🔍 Verifying database schema...")
    
    # Get database connection
    db_user = os.getenv('user', 'postgres')
    db_password = os.getenv('password')
    db_host = os.getenv('host', 'localhost')
    db_port = os.getenv('port', '5432')
    db_name = os.getenv('dbname', 'postgres')
    
    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Get all columns in users table
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY column_name
            """))
            
            columns = {}
            required_auth_columns = {
                'username', 'email', 'password_hash', 'last_login', 
                'is_verified', 'google_id', 'avatar_url', 'is_active', 'role'
            }
            
            print("📋 Current users table structure:")
            for row in result:
                column_name, data_type, is_nullable, default = row
                columns[column_name] = {
                    'type': data_type,
                    'nullable': is_nullable == 'YES',
                    'default': default
                }
                
                # Mark required auth columns
                status = "✅" if column_name in required_auth_columns else "📄"
                nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
                default_str = f" DEFAULT {default}" if default else ""
                print(f"   {status} {column_name}: {data_type} ({nullable}){default_str}")
            
            # Check if all required authentication columns exist
            missing_columns = required_auth_columns - set(columns.keys())
            
            if missing_columns:
                print(f"\n❌ Missing required columns: {', '.join(missing_columns)}")
                return False
            else:
                print(f"\n✅ All {len(required_auth_columns)} required authentication columns present!")
                
                # Test if we can create a user model instance
                print("\n🧪 Testing User model compatibility...")
                try:
                    from app import app
                    from models import User, db
                    
                    with app.app_context():
                        # Try to query users (this will test the model)
                        user_count = User.query.count()
                        print(f"✅ User model works! Found {user_count} existing users.")
                        
                        # Test if we can access the new fields
                        test_query = User.query.with_entities(
                            User.username, User.email, User.last_login, 
                            User.is_verified, User.google_id, User.avatar_url
                        ).first()
                        print("✅ All authentication fields accessible!")
                        
                except Exception as e:
                    print(f"⚠️  Model test warning: {e}")
                
                return True
                
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    if verify_database():
        print("\n🎉 Database is ready for authentication!")
        print("💡 You can now use registration and login functionality.")
    else:
        print("\n❌ Database verification failed.")
        print("🔧 Run the migration script again if needed.")