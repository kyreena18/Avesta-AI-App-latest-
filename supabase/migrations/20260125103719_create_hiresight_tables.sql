/*
  # Create HireSight Platform Tables

  1. New Tables
    - `jobs`
      - `id` (bigint, primary key, auto-increment)
      - `title` (text, required) - Job title
      - `description` (text) - Job description
      - `requirements` (text) - Job requirements
      - `skills` (text) - Required skills (comma-separated)
      - `min_experience` (integer) - Minimum years of experience
      - `education_levels` (text) - Required education levels
      - `status` (text, default 'active') - Job status (active, closed, on-hold)
      - `created_at` (timestamptz, default now())
      - `updated_at` (timestamptz, default now())
    
    - `shortlists`
      - `id` (bigint, primary key, auto-increment)
      - `resume_id` (text, required) - Resume identifier
      - `job_id` (bigint) - Reference to jobs table
      - `status` (text, default 'shortlisted') - Status (shortlisted, rejected, etc.)
      - `created_at` (timestamptz, default now())
    
    - `notes`
      - `id` (bigint, primary key, auto-increment)
      - `resume_id` (text, required) - Resume identifier
      - `job_id` (bigint) - Reference to jobs table
      - `note_text` (text, required) - Note content
      - `created_at` (timestamptz, default now())
    
    - `interviews`
      - `id` (bigint, primary key, auto-increment)
      - `resume_id` (text, required) - Resume identifier
      - `job_id` (bigint) - Reference to jobs table
      - `scheduled_date` (timestamptz, required) - Interview date and time
      - `interview_type` (text, default 'phone') - Type (phone, video, in-person)
      - `status` (text, default 'scheduled') - Status (scheduled, completed, cancelled)
      - `notes` (text) - Interview notes
      - `created_at` (timestamptz, default now())
      - `updated_at` (timestamptz, default now())

  2. Security
    - Enable RLS on all tables
    - Add policies for authenticated users to manage all data
    - Users can perform all operations (select, insert, update, delete) on all tables
    
  3. Important Notes
    - All tables use auto-incrementing IDs
    - Foreign key references to jobs table are optional (allow NULL)
    - Timestamps are automatically managed
    - RLS policies allow authenticated users full access to the platform
*/

-- Create jobs table
CREATE TABLE IF NOT EXISTS jobs (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  title text NOT NULL,
  description text DEFAULT '',
  requirements text DEFAULT '',
  skills text DEFAULT '',
  min_experience integer DEFAULT 0,
  education_levels text DEFAULT '',
  status text DEFAULT 'active',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create shortlists table
CREATE TABLE IF NOT EXISTS shortlists (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  resume_id text NOT NULL,
  job_id bigint REFERENCES jobs(id) ON DELETE CASCADE,
  status text DEFAULT 'shortlisted',
  created_at timestamptz DEFAULT now()
);

-- Create notes table
CREATE TABLE IF NOT EXISTS notes (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  resume_id text NOT NULL,
  job_id bigint REFERENCES jobs(id) ON DELETE CASCADE,
  note_text text NOT NULL,
  created_at timestamptz DEFAULT now()
);

-- Create interviews table
CREATE TABLE IF NOT EXISTS interviews (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  resume_id text NOT NULL,
  job_id bigint REFERENCES jobs(id) ON DELETE CASCADE,
  scheduled_date timestamptz NOT NULL,
  interview_type text DEFAULT 'phone',
  status text DEFAULT 'scheduled',
  notes text DEFAULT '',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Enable Row Level Security
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE shortlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;

-- Create policies for jobs table
CREATE POLICY "Authenticated users can view all jobs"
  ON jobs FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can create jobs"
  ON jobs FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Authenticated users can update jobs"
  ON jobs FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Authenticated users can delete jobs"
  ON jobs FOR DELETE
  TO authenticated
  USING (true);

-- Create policies for shortlists table
CREATE POLICY "Authenticated users can view all shortlists"
  ON shortlists FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can create shortlists"
  ON shortlists FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Authenticated users can update shortlists"
  ON shortlists FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Authenticated users can delete shortlists"
  ON shortlists FOR DELETE
  TO authenticated
  USING (true);

-- Create policies for notes table
CREATE POLICY "Authenticated users can view all notes"
  ON notes FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can create notes"
  ON notes FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Authenticated users can update notes"
  ON notes FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Authenticated users can delete notes"
  ON notes FOR DELETE
  TO authenticated
  USING (true);

-- Create policies for interviews table
CREATE POLICY "Authenticated users can view all interviews"
  ON interviews FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can create interviews"
  ON interviews FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Authenticated users can update interviews"
  ON interviews FOR UPDATE
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Authenticated users can delete interviews"
  ON interviews FOR DELETE
  TO authenticated
  USING (true);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_shortlists_resume_id ON shortlists(resume_id);
CREATE INDEX IF NOT EXISTS idx_shortlists_job_id ON shortlists(job_id);
CREATE INDEX IF NOT EXISTS idx_notes_resume_id ON notes(resume_id);
CREATE INDEX IF NOT EXISTS idx_notes_job_id ON notes(job_id);
CREATE INDEX IF NOT EXISTS idx_interviews_resume_id ON interviews(resume_id);
CREATE INDEX IF NOT EXISTS idx_interviews_job_id ON interviews(job_id);
CREATE INDEX IF NOT EXISTS idx_interviews_scheduled_date ON interviews(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);