-- =====================================================
-- HIRESIGHT PLATFORM - SUPABASE SCHEMA
-- Copy and paste this entire file into Supabase SQL Editor
-- =====================================================
--
-- IMPORTANT NOTE: Supabase Auth automatically creates and manages
-- the auth.users table for storing user credentials (email, password hash).
-- You do NOT need to create a users table for authentication.
-- This SQL creates additional tables for your application data.
-- =====================================================

-- Optional: Custom users table for additional profile data
-- This links to auth.users via user_id (UUID from auth.users)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT,
    email TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see and update their own profile
DROP POLICY IF EXISTS "Users can view own profile" ON users;
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON users;
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

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

-- Trigger to create user profile on signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    requirements TEXT,
    skills TEXT,
    min_experience INTEGER DEFAULT 0,
    education_levels TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shortlists table
CREATE TABLE IF NOT EXISTS shortlists (
    id BIGSERIAL PRIMARY KEY,
    resume_id TEXT NOT NULL,
    job_id BIGINT REFERENCES jobs(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'shortlisted',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Notes table
CREATE TABLE IF NOT EXISTS notes (
    id BIGSERIAL PRIMARY KEY,
    resume_id TEXT NOT NULL,
    job_id BIGINT REFERENCES jobs(id) ON DELETE CASCADE,
    note_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Interviews table
CREATE TABLE IF NOT EXISTS interviews (
    id BIGSERIAL PRIMARY KEY,
    resume_id TEXT NOT NULL,
    job_id BIGINT REFERENCES jobs(id) ON DELETE CASCADE,
    scheduled_date TIMESTAMPTZ,
    interview_type TEXT DEFAULT 'phone',
    status TEXT DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_shortlists_job_id ON shortlists(job_id);
CREATE INDEX IF NOT EXISTS idx_shortlists_resume_id ON shortlists(resume_id);
CREATE INDEX IF NOT EXISTS idx_notes_resume_id ON notes(resume_id);
CREATE INDEX IF NOT EXISTS idx_notes_job_id ON notes(job_id);
CREATE INDEX IF NOT EXISTS idx_interviews_resume_id ON interviews(resume_id);
CREATE INDEX IF NOT EXISTS idx_interviews_job_id ON interviews(job_id);

-- Enable Row Level Security (RLS)
-- Note: users table RLS is already enabled above
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE shortlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated users
-- Jobs policies
DROP POLICY IF EXISTS "Allow all for authenticated users" ON jobs;
CREATE POLICY "Allow all for authenticated users" ON jobs
    FOR ALL USING (auth.role() = 'authenticated');

-- Shortlists policies
DROP POLICY IF EXISTS "Allow all for authenticated users" ON shortlists;
CREATE POLICY "Allow all for authenticated users" ON shortlists
    FOR ALL USING (auth.role() = 'authenticated');

-- Notes policies
DROP POLICY IF EXISTS "Allow all for authenticated users" ON notes;
CREATE POLICY "Allow all for authenticated users" ON notes
    FOR ALL USING (auth.role() = 'authenticated');

-- Interviews policies
DROP POLICY IF EXISTS "Allow all for authenticated users" ON interviews;
CREATE POLICY "Allow all for authenticated users" ON interviews
    FOR ALL USING (auth.role() = 'authenticated');

-- =====================================================
-- Done! All tables created successfully.
-- =====================================================
