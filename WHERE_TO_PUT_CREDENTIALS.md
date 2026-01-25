# Where to Put Supabase URL and Anon Key

## Option 1: Edit supabase_config.py (Easiest)

Open `supabase_config.py` and replace the placeholder values:

```python
EXPO_PUBLIC_SUPABASE_URL=https://tmsdbspxhujrwqrptcry.supabase.co

EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRtc2Ric3B4aHVqcndxcnB0Y3J5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg3MTA4NDUsImV4cCI6MjA4NDI4Njg0NX0.0XkPU2hWqtxTg_k-Pj_2bBgtLVrLDht68t98DLbu2Ew
```

**Example:**
```python
SUPABASE_URL = "https://abcdefghijklmnop.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYxNzI5MzI4OCwiZXhwIjoxOTMyODcwODg4fQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## Option 2: Environment Variables (More Secure)

Set environment variables in PowerShell:

```powershell
$env:SUPABASE_URL = "https://your-project-id.supabase.co"
$env:SUPABASE_KEY = "your-anon-key-here"
```

Or set them permanently (for current user):
```powershell
[System.Environment]::SetEnvironmentVariable("SUPABASE_URL", "https://your-project-id.supabase.co", "User")
[System.Environment]::SetEnvironmentVariable("SUPABASE_KEY", "your-anon-key-here", "User")
```

## How to Get Your Credentials

1. Go to https://app.supabase.com
2. Sign in and select your project
3. Click **Settings** (gear icon) in the left sidebar
4. Click **API** under Project Settings
5. You'll see:
   - **Project URL** - Copy this (starts with `https://`)
   - **anon public** key - Copy this (long string starting with `eyJ...`)

## Important Notes

- Use the **anon public** key (NOT the service_role key)
- The anon key is safe to use in frontend/client code
- Keep your service_role key secret (only for backend/server use)
- The URL format is: `https://[project-id].supabase.co`

## Quick Copy-Paste Template

After getting your credentials from Supabase dashboard:

```python
# In supabase_config.py
SUPABASE_URL="https://tmsdbspxhujrwqrptcry.supabase.co"

SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRtc2Ric3B4aHVqcndxcnB0Y3J5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg3MTA4NDUsImV4cCI6MjA4NDI4Njg0NX0.0XkPU2hWqtxTg_k-Pj_2bBgtLVrLDht68t98DLbu2Ew"
```

Replace the placeholder text with your actual values!
