# HireSight Platform - Quick Start Guide

## What's New

You now have a **complete recruiter ATS platform** built around your existing HireSight AI resume matching engine.

## Key Files

- **`platform_app.py`** - Main application (run this!)
- **`hiresight_engine.py`** - Wrapper around your existing HireSight logic (preserved as black box)
- **`database.py`** - SQLite database for jobs, notes, interviews
- **`templates/`** - All HTML templates with modern UI
- **`static/platform.css`** - Modern CSS styling

## How to Run

1. Make sure dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the platform:
   ```bash
   python platform_app.py
   ```

3. Open browser to: `http://localhost:5000`

4. Login with any credentials (demo mode)

## What You Get

### ✅ All Required Modules

1. **Dashboard** - Statistics and quick actions
2. **Resume Repository** - View all resumes, download, view notes
3. **Resume Upload** - Upload PDF/DOCX, auto-process and index
4. **Resume Search** - Job Description, Skills, Education search
5. **Job Openings** - Create jobs, auto-match resumes
6. **Shortlisting & Notes** - Shortlist/reject, add notes
7. **Interview Scheduler** - Schedule and track interviews

### ✅ UI Features

- Modern sidebar navigation
- Card-based resume UI
- Clean, professional design
- Loading states
- Flash messages
- Responsive layout

## Important Notes

- **Your existing HireSight AI logic is 100% preserved**
- All search, embedding, and scoring functions remain unchanged
- The platform wraps around your engine, doesn't replace it
- Original resume files are preserved
- Database (SQLite) auto-creates on first run

## Navigation

Use the sidebar to navigate:
- 📊 Dashboard
- 📁 Resume Repository  
- ⬆️ Upload Resume
- 🔍 Search Resumes
- 💼 Job Openings
- 📅 Interviews

## Next Steps

1. Upload some resumes using "Upload Resume"
2. Create a job opening in "Job Openings"
3. View matched candidates for the job
4. Shortlist candidates and add notes
5. Schedule interviews

Everything is ready to use!
