-- Fix Supabase Database Schema - Add Missing Columns
-- Run this in your Supabase SQL Editor

-- Add missing created_by column to documents table
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS created_by TEXT;

-- Add missing created_by_id column (for user ID references if using auth)
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS created_by_id UUID REFERENCES auth.users(id) ON DELETE SET NULL;

-- Add missing invitation fields
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS invitation_sent BOOLEAN DEFAULT FALSE;

ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS invitation_sent_at TIMESTAMPTZ NULL;

-- Add missing user2_email field for workflow
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS user2_email TEXT;

-- Add missing field_assignments for tracking
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS field_assignments JSONB DEFAULT '{}';

-- Create index for better performance on new columns
CREATE INDEX IF NOT EXISTS idx_documents_created_by ON documents(created_by);
CREATE INDEX IF NOT EXISTS idx_documents_created_by_id ON documents(created_by_id);
CREATE INDEX IF NOT EXISTS idx_documents_user2_email ON documents(user2_email);

-- Update RLS policies to include new columns
-- (The existing policies should still work, but we can add more specific ones if needed)

-- Add a function to get documents safely (for the app to use)
CREATE OR REPLACE FUNCTION get_user_documents(user_identifier TEXT DEFAULT NULL)
RETURNS TABLE (
    id UUID,
    name TEXT,
    status TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ,
    created_by TEXT,
    user1_data JSONB,
    user2_data JSONB,
    invitation_sent BOOLEAN,
    file_path TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.name,
        d.status,
        d.created_at,
        d.updated_at,
        d.created_by,
        d.user1_data,
        d.user2_data,
        d.invitation_sent,
        d.file_path
    FROM documents d
    WHERE 
        user_identifier IS NULL 
        OR d.created_by = user_identifier 
        OR d.created_by_id::text = user_identifier
    ORDER BY d.created_at DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission to authenticated and anonymous users
GRANT EXECUTE ON FUNCTION get_user_documents TO authenticated;
GRANT EXECUTE ON FUNCTION get_user_documents TO anon;

-- Verify the schema changes
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'documents' 
ORDER BY ordinal_position;