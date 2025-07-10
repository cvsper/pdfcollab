-- PDF Collaboration System - Supabase Schema
-- Run these SQL commands in your Supabase SQL editor

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ NULL,
    file_path TEXT,
    original_filename TEXT,
    file_size INTEGER,
    user1_data JSONB DEFAULT '{}',
    user2_data JSONB DEFAULT '{}',
    supporting_docs JSONB DEFAULT '[]'
);

-- Template documents table for storing pre-uploaded PDFs
CREATE TABLE IF NOT EXISTS template_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    file_data BYTEA NOT NULL,
    filename TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    content_type TEXT DEFAULT 'application/pdf',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- PDF fields table
CREATE TABLE IF NOT EXISTS pdf_fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    field_name TEXT NOT NULL,
    field_type TEXT NOT NULL DEFAULT 'text',
    field_value TEXT,
    assigned_to TEXT NOT NULL,
    position_x REAL DEFAULT 0,
    position_y REAL DEFAULT 0,
    width REAL DEFAULT 0,
    height REAL DEFAULT 0,
    page_number INTEGER DEFAULT 0,
    source TEXT DEFAULT 'extracted',
    pdf_field_name TEXT,
    is_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Field configurations table for custom field definitions
CREATE TABLE IF NOT EXISTS field_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    field_id UUID NOT NULL REFERENCES pdf_fields(id) ON DELETE CASCADE,
    configuration JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Document templates table
CREATE TABLE IF NOT EXISTS document_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    field_definitions JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    document_id UUID REFERENCES documents(id) ON DELETE SET NULL,
    user_type TEXT,
    action TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);
CREATE INDEX IF NOT EXISTS idx_pdf_fields_document_id ON pdf_fields(document_id);
CREATE INDEX IF NOT EXISTS idx_pdf_fields_assigned_to ON pdf_fields(assigned_to);
CREATE INDEX IF NOT EXISTS idx_pdf_fields_page ON pdf_fields(page_number);
CREATE INDEX IF NOT EXISTS idx_audit_log_document_id ON audit_log(document_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);

-- Row Level Security (RLS) policies
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE pdf_fields ENABLE ROW LEVEL SECURITY;
ALTER TABLE field_configurations ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- Basic policies (adjust based on your authentication requirements)
-- For now, allowing all operations for authenticated users
CREATE POLICY "Enable all operations for authenticated users" ON documents
    FOR ALL TO authenticated USING (true);

CREATE POLICY "Enable all operations for authenticated users" ON pdf_fields
    FOR ALL TO authenticated USING (true);

CREATE POLICY "Enable all operations for authenticated users" ON field_configurations
    FOR ALL TO authenticated USING (true);

CREATE POLICY "Enable all operations for authenticated users" ON document_templates
    FOR ALL TO authenticated USING (true);

CREATE POLICY "Enable all operations for authenticated users" ON audit_log
    FOR ALL TO authenticated USING (true);

-- Public access for anonymous users (adjust as needed)
CREATE POLICY "Enable read access for anonymous users" ON documents
    FOR SELECT TO anon USING (true);

CREATE POLICY "Enable read access for anonymous users" ON pdf_fields
    FOR SELECT TO anon USING (true);

CREATE POLICY "Enable insert for anonymous users" ON documents
    FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "Enable insert for anonymous users" ON pdf_fields
    FOR INSERT TO anon WITH CHECK (true);

CREATE POLICY "Enable update for anonymous users" ON documents
    FOR UPDATE TO anon USING (true);

CREATE POLICY "Enable update for anonymous users" ON pdf_fields
    FOR UPDATE TO anon USING (true);

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pdf_fields_updated_at BEFORE UPDATE ON pdf_fields 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_document_templates_updated_at BEFORE UPDATE ON document_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- User authentication tables
-- Users table for authentication and user management
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user', -- 'user' or 'admin'
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ NULL,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ NULL
);

-- User documents association for access control
CREATE TABLE IF NOT EXISTS user_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- 'owner', 'user1', 'user2', 'viewer'
    can_edit BOOLEAN DEFAULT true,
    can_share BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    UNIQUE(user_id, document_id)
);

-- Document invitations for sharing documents with users
CREATE TABLE IF NOT EXISTS document_invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    invited_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invited_email VARCHAR(255) NOT NULL,
    invited_user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- 'user1', 'user2', 'viewer'
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    accepted_at TIMESTAMPTZ NULL,
    declined_at TIMESTAMPTZ NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User sessions for tracking active sessions
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW()
);

-- Add owner_id to documents table
ALTER TABLE documents ADD COLUMN IF NOT EXISTS owner_id UUID REFERENCES users(id);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES users(id);

-- Add user tracking to audit log
ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id);
ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS ip_address INET;

-- Create indexes for authentication tables
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_user_documents_user_id ON user_documents(user_id);
CREATE INDEX IF NOT EXISTS idx_user_documents_document_id ON user_documents(document_id);
CREATE INDEX IF NOT EXISTS idx_user_documents_role ON user_documents(role);
CREATE INDEX IF NOT EXISTS idx_document_invitations_document_id ON document_invitations(document_id);
CREATE INDEX IF NOT EXISTS idx_document_invitations_invited_email ON document_invitations(invited_email);
CREATE INDEX IF NOT EXISTS idx_document_invitations_token ON document_invitations(token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_documents_owner_id ON documents(owner_id);

-- Enable RLS for new tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_invitations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Users can view their own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Admins can view all users" ON users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins can manage all users" ON users
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- RLS Policies for user_documents table
CREATE POLICY "Users can view their document associations" ON user_documents
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Document owners can manage associations" ON user_documents
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM documents d 
            WHERE d.id = document_id AND d.owner_id = auth.uid()
        )
    );

CREATE POLICY "Admins can view all document associations" ON user_documents
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- RLS Policies for document_invitations table
CREATE POLICY "Users can view invitations sent to them" ON document_invitations
    FOR SELECT USING (
        invited_email = (SELECT email FROM users WHERE id = auth.uid())
        OR invited_user_id = auth.uid()
    );

CREATE POLICY "Document owners can manage invitations" ON document_invitations
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM documents d 
            WHERE d.id = document_id AND d.owner_id = auth.uid()
        )
    );

-- RLS Policies for user_sessions table
CREATE POLICY "Users can view their own sessions" ON user_sessions
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can delete their own sessions" ON user_sessions
    FOR DELETE USING (user_id = auth.uid());

-- Update documents policies to include ownership
DROP POLICY IF EXISTS "Enable all operations for authenticated users" ON documents;
DROP POLICY IF EXISTS "Enable read access for anonymous users" ON documents;
DROP POLICY IF EXISTS "Enable insert for anonymous users" ON documents;
DROP POLICY IF EXISTS "Enable update for anonymous users" ON documents;

CREATE POLICY "Users can view their own documents" ON documents
    FOR SELECT USING (
        owner_id = auth.uid() 
        OR EXISTS (
            SELECT 1 FROM user_documents ud 
            WHERE ud.document_id = id AND ud.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create documents" ON documents
    FOR INSERT WITH CHECK (owner_id = auth.uid());

CREATE POLICY "Document owners can update their documents" ON documents
    FOR UPDATE USING (owner_id = auth.uid());

CREATE POLICY "Document owners can delete their documents" ON documents
    FOR DELETE USING (owner_id = auth.uid());

CREATE POLICY "Admins can view all documents" ON documents
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Admins can manage all documents" ON documents
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Add triggers for new tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to clean up expired sessions and invitations
CREATE OR REPLACE FUNCTION cleanup_expired_records()
RETURNS void AS $$
BEGIN
    -- Clean up expired sessions
    DELETE FROM user_sessions WHERE expires_at < NOW();
    
    -- Clean up expired invitations
    DELETE FROM document_invitations WHERE expires_at < NOW() AND accepted_at IS NULL;
    
    -- Reset login attempts for users whose lockout has expired
    UPDATE users SET login_attempts = 0, locked_until = NULL 
    WHERE locked_until IS NOT NULL AND locked_until < NOW();
END;
$$ LANGUAGE plpgsql;

-- Create a scheduled job to run cleanup (if using pg_cron extension)
-- SELECT cron.schedule('cleanup-expired-records', '0 */6 * * *', 'SELECT cleanup_expired_records();');