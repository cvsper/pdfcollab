-- Fix Supabase Database Schema - Add Missing Columns (Simplified Version)
-- Run this in your Supabase SQL Editor

-- Add missing created_by column to documents table
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS created_by TEXT;

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
CREATE INDEX IF NOT EXISTS idx_documents_user2_email ON documents(user2_email);

-- Verify the schema changes
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'documents' 
ORDER BY ordinal_position;