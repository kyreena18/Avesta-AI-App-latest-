# How to Run the Avesta AI Platform

## Quick Start Guide

### Step 1: Check Your Environment

First, verify if your existing `web_app.py` works (this will tell us if dependencies are compatible):

```powershell
python web_app.py
```

If `web_app.py` runs successfully, then `platform_app.py` will also work once dependencies are aligned.

### Step 2: Fix Dependencies (If Needed)

If you get import errors, try one of these solutions:

#### Option A: Install Compatible Versions

```powershell
pip install sentence-transformers==2.2.2 "transformers<4.35.0" "huggingface_hub<0.20.0"
```

#### Option B: Use Requirements File

```powershell
pip install -r requirements.txt
```

### Step 3: Run the Platform

Once dependencies are working:

```powershell
python platform_app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

### Step 4: Access the Platform

1. Open your browser
2. Go to: `http://localhost:5000`
3. Login with any credentials (demo mode - accepts any username/password)

## Troubleshooting

### If you get dependency errors:

1. **Check what versions you have:**
   ```powershell
   pip list | Select-String "sentence|transformers|huggingface"
   ```

2. **If web_app.py works but platform_app.py doesn't:**
   - They use the same dependencies, so if one works, the other should too
   - Try running: `python -c "import avesta_engine"` to test

3. **Create a virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python platform_app.py
   ```

## What You'll See

1. **Login Page** - Enter any username/password
2. **Dashboard** - Overview with statistics
3. **Sidebar Navigation** - Access all modules:
   - 📊 Dashboard
   - 📁 Resume Repository
   - ⬆️ Upload Resume
   - 🔍 Search Resumes
   - 💼 Job Openings
   - 📅 Interviews

## First Steps After Login

1. Upload a resume (if you have PDF/DOCX files)
2. Create a job opening
3. View matched candidates
4. Try searching resumes

Everything is ready to use!
