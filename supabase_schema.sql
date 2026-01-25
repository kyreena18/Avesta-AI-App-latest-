-- Supabase SQL Schema for HireSight Platform
-- Run this in your Supabase SQL Editor to create the tables

-- Enable UUID extension (if not already enabled)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_shortlists_job_id ON shortlists(job_id);
CREATE INDEX IF NOT EXISTS idx_shortlists_resume_id ON shortlists(resume_id);
CREATE INDEX IF NOT EXISTS idx_notes_resume_id ON notes(resume_id);
CREATE INDEX IF NOT EXISTS idx_notes_job_id ON notes(job_id);
CREATE INDEX IF NOT EXISTS idx_interviews_resume_id ON interviews(resume_id);
CREATE INDEX IF NOT EXISTS idx_interviews_job_id ON interviews(job_id);

-- Enable Row Level Security (RLS) - Optional but recommended
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE shortlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust based on your security requirements)
-- For now, allow all operations for authenticated users
-- You can make this more restrictive later

-- Jobs policies
CREATE POLICY "Allow all for authenticated users" ON jobs
    FOR ALL USING (auth.role() = 'authenticated');

-- Shortlists policies
CREATE POLICY "Allow all for authenticated users" ON shortlists
    FOR ALL USING (auth.role() = 'authenticated');

-- Notes policies
CREATE POLICY "Allow all for authenticated users" ON notes
    FOR ALL USING (auth.role() = 'authenticated');

-- Interviews policies
CREATE POLICY "Allow all for authenticated users" ON interviews
    FOR ALL USING (auth.role() = 'authenticated');
