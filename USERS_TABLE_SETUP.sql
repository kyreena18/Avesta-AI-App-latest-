-- =====================================================
-- USERS TABLE SETUP FOR SUPABASE
-- Copy and paste this into Supabase SQL Editor
-- =====================================================
--
-- IMPORTANT: Supabase Auth automatically creates the auth.users table
-- for storing credentials (email, password hash). You don't need to
-- create that table manually. This SQL creates an optional custom
-- users table for storing additional profile information.
-- =====================================================

-- Custom users table for additional profile data
-- This links to auth.users via user_id (UUID from auth.users)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT,
    email TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own profile
DROP POLICY IF EXISTS "Users can view own profile" ON users;
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

-- Policy: Users can update their own profile
DROP POLICY IF EXISTS "Users can update own profile" ON users;
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Policy: Users can insert their own profile (for trigger)
DROP POLICY IF EXISTS "Users can insert own profile" ON users;
CREATE POLICY "Users can insert own profile" ON users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Function to automatically create user profile when user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1))
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically create user profile when user signs up
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- =====================================================
-- Done! The users table is now set up.
-- 
-- How it works:
-- 1. When a user registers via Supabase Auth, they are automatically
--    added to auth.users table (handled by Supabase)
-- 2. The trigger automatically creates a corresponding row in the
--    public.users table with their profile information
-- 3. The user's credentials (email, password hash) are stored in
--    auth.users (automatic, no SQL needed)
-- =====================================================
