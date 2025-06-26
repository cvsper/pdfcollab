#!/usr/bin/env python3
"""
Database migration script to add authentication fields to User table
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, DateTime, Boolean
from sqlalchemy.exc import OperationalError, ProgrammingError

load_dotenv()

def get_database_url():
    """Get database URL from environment"""
    # Try PostgreSQL first (Supabase)
    db_user = os.getenv('user', 'postgres')
    db_password = os.getenv('password')
    db_host = os.getenv('host', 'localhost')
    db_port = os.getenv('port', '5432')
    db_name = os.getenv('dbname', 'postgres')
    
    if all([db_user, db_password, db_host, db_port, db_name]):
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        # Fallback to SQLite
        return 'sqlite:///pdf_collaborator.db'

def migrate_database():
    """Add missing authentication fields to User table"""
    print("🔄 Starting database migration for authentication fields...")
    
    # Get database connection
    database_url = get_database_url()
    print(f"📊 Connecting to database: {database_url.split('@')[1] if '@' in database_url else database_url}")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Check if we're using PostgreSQL or SQLite
            is_postgres = 'postgresql' in database_url
            
            print("🔍 Checking existing table structure...")
            
            # Get current columns
            if is_postgres:
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users'
                """))
            else:
                result = conn.execute(text("PRAGMA table_info(users)"))
            
            existing_columns = set()
            for row in result:
                if is_postgres:
                    existing_columns.add(row[0])
                else:
                    existing_columns.add(row[1])  # SQLite returns (cid, name, type, ...)
            
            print(f"📋 Found existing columns: {', '.join(sorted(existing_columns))}")
            
            # Define new columns to add
            new_columns = {
                'last_login': 'TIMESTAMP',
                'is_verified': 'BOOLEAN DEFAULT FALSE',
                'google_id': 'VARCHAR(100)',
                'avatar_url': 'VARCHAR(500)'
            }
            
            # Add missing columns
            columns_added = 0
            for column_name, column_type in new_columns.items():
                if column_name not in existing_columns:
                    try:
                        if is_postgres:
                            sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                        else:
                            sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                        
                        print(f"➕ Adding column: {column_name} ({column_type})")
                        conn.execute(text(sql))
                        conn.commit()
                        columns_added += 1
                        
                    except (OperationalError, ProgrammingError) as e:
                        print(f"⚠️  Warning: Could not add column {column_name}: {e}")
                        continue
                else:
                    print(f"✅ Column {column_name} already exists")
            
            # Update password_hash column to allow NULL for OAuth users
            try:
                if 'password_hash' in existing_columns:
                    if is_postgres:
                        conn.execute(text("ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL"))
                        conn.commit()
                        print("✅ Updated password_hash to allow NULL (for OAuth users)")
                    else:
                        print("ℹ️  SQLite doesn't support ALTER COLUMN - password_hash constraints unchanged")
            except Exception as e:
                print(f"⚠️  Could not update password_hash constraints: {e}")
            
            # Add unique constraints if needed
            try:
                if 'google_id' in new_columns and 'google_id' not in existing_columns:
                    if is_postgres:
                        conn.execute(text("CREATE UNIQUE INDEX CONCURRENTLY idx_users_google_id ON users(google_id) WHERE google_id IS NOT NULL"))
                        conn.commit()
                        print("✅ Added unique index for google_id")
            except Exception as e:
                print(f"⚠️  Could not add unique constraint for google_id: {e}")
            
            print(f"\n✅ Migration completed! Added {columns_added} new columns.")
            
            # Verify the migration
            print("\n🔍 Verifying migration...")
            if is_postgres:
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = 'users'
                    ORDER BY column_name
                """))
                print("📋 Final table structure:")
                for row in result:
                    nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                    print(f"   - {row[0]}: {row[1]} ({nullable})")
            else:
                result = conn.execute(text("PRAGMA table_info(users)"))
                print("📋 Final table structure:")
                for row in result:
                    nullable = "NULL" if row[3] == 0 else "NOT NULL"
                    print(f"   - {row[1]}: {row[2]} ({nullable})")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check database connection settings in .env")
        print("2. Ensure database server is running")
        print("3. Verify user has ALTER TABLE permissions")
        print("4. For SQLite: check file permissions")
        return False
    
    print("\n🎉 Database migration completed successfully!")
    print("💡 You can now restart your Flask application.")
    return True

if __name__ == "__main__":
    migrate_database()