# Quick Start: Supabase Integration

## 1. Install Supabase Client

```powershell
pip install supabase
```

## 2. Get Your Supabase Credentials

1. Go to https://app.supabase.com
2. Create/select your project
3. Go to Settings → API
4. Copy:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **Anon Key** (long string starting with `eyJ...`)

## 3. Set Environment Variables

```powershell
$env:SUPABASE_URL = "https://your-project.supabase.co"
$env:SUPABASE_KEY = "your-anon-key-here"
```

Or edit `supabase_config.py` directly.

## 4. Create Database Tables

1. In Supabase dashboard, go to **SQL Editor**
2. Copy and paste the entire contents of `supabase_schema.sql`
3. Click **Run**

This creates all tables: jobs, shortlists, notes, interviews

## 5. Enable Authentication

1. Go to **Authentication** → **Providers**
2. **Email** provider should already be enabled
3. Configure email settings if needed (optional)

## 6. Switch to Supabase Version

Rename files:
- `platform_app.py` → `platform_app_sqlite.py` (backup)
- `platform_app_supabase.py` → `platform_app.py`

Or update imports in `platform_app.py`:
```python
# Change this:
import database

# To this:
import database_supabase as database
```

And update the login route to use Supabase auth.

## 7. Test It

```powershell
python platform_app.py
```

Then:
1. Go to http://localhost:5000
2. Click "Register" to create an account
3. Login with your credentials
4. Create a job opening to test database connection

## Troubleshooting

**Connection Error?**
- Check your SUPABASE_URL and SUPABASE_KEY
- Make sure you're using the Anon key (not service role key)

**Auth Error?**
- Make sure Email provider is enabled in Supabase
- Check Supabase logs in the dashboard

**Table Errors?**
- Run the SQL schema again
- Check table permissions in Supabase dashboard

## Benefits

✅ Real user accounts and authentication
✅ Data stored in cloud (Supabase)
✅ Automatic backups
✅ Scalable infrastructure
✅ Web dashboard to view/manage data
✅ Row Level Security for data protection
