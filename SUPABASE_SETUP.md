# Supabase Integration Guide for HireSight Platform

This guide will help you connect HireSight to Supabase for storing job openings, interviews, and user authentication.

## Prerequisites

1. A Supabase account (sign up at https://supabase.com)
2. A new Supabase project created
3. Python `supabase` package installed

## Step 1: Install Supabase Python Client

```powershell
pip install supabase
```

## Step 2: Set Up Supabase Project

1. Go to https://app.supabase.com
2. Create a new project (or use existing)
3. Go to Project Settings → API
4. Copy your:
   - Project URL
   - Anon (public) key

## Step 3: Create Database Tables

1. Go to your Supabase project
2. Navigate to SQL Editor
3. Run the SQL from `supabase_schema.sql` to create all tables

Alternatively, you can create tables manually:
- `jobs` - Job openings
- `shortlists` - Shortlisted resumes
- `notes` - Recruiter notes
- `interviews` - Scheduled interviews

## Step 4: Configure Credentials

Option A: Environment Variables (Recommended)
```powershell
# Set environment variables
$env:SUPABASE_URL = "https://your-project.supabase.co"
$env:SUPABASE_KEY = "your-anon-key-here"
```

Option B: Update supabase_config.py directly
```python
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
```

## Step 5: Enable Authentication

1. Go to Authentication → Providers in Supabase dashboard
2. Enable Email provider (default, usually already enabled)
3. Configure email settings if needed

## Step 6: Update platform_app.py

You'll need to update `platform_app.py` to:
1. Import `database_supabase` instead of `database`
2. Use Supabase auth instead of session-based login
3. Update login/logout routes

See `platform_app_supabase.py` for the updated version.

## Database Schema

The schema includes:
- `jobs` - Job openings with title, description, requirements, etc.
- `shortlists` - Resume shortlisting with job associations
- `notes` - Recruiter notes linked to resumes/jobs
- `interviews` - Interview scheduling and tracking

All tables include proper indexes and Row Level Security (RLS) policies.

## Migration from SQLite

If you have existing data in SQLite:
1. Export data from SQLite database
2. Import into Supabase using the SQL Editor or API
3. Or run a migration script to transfer data

## Testing

After setup, test the connection:
```python
python -c "from supabase_config import supabase; print('Connected!')"
```

## Benefits of Supabase

- ✅ Real-time database updates
- ✅ Built-in authentication
- ✅ Row Level Security
- ✅ Automatic backups
- ✅ Scalable hosting
- ✅ Easy API access
- ✅ Web dashboard for data management

## Next Steps

1. Complete the setup steps above
2. Test authentication
3. Test creating jobs and interviews
4. Migrate existing data if needed
