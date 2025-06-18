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