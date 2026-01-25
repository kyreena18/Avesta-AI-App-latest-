# HireSight Platform - Recruiter ATS Platform

A modern, recruiter-focused ATS platform built around the existing HireSight AI resume matching engine.

## Features

### Core Modules

1. **Recruiter Workspace**
   - Simple login/session system
   - Dashboard with statistics
   - Sidebar navigation

2. **Resume Repository**
   - View all indexed resumes
   - Resume cards with preview
   - Download original files
   - View notes

3. **Resume Upload**
   - Upload PDF/DOCX files
   - Automatic text extraction
   - Automatic indexing using HireSight engine
   - Immediate availability in repository

4. **Resume Search**
   - Job Description search
   - Skills & Experience search
   - Education Level search
   - Uses existing HireSight AI matching logic

5. **Job Openings**
   - Create job openings with requirements
   - Automatic resume matching
   - View matched candidates
   - Track job status

6. **Shortlisting & Notes**
   - Shortlist/reject resumes per job
   - Add recruiter notes
   - View notes by resume or job

7. **Interview Scheduler**
   - Schedule interviews
   - Track interview status
   - Link interviews to jobs and resumes

## Installation

1. Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

2. The platform uses the existing HireSight AI engine, so all resume processing logic is preserved.

3. Database (SQLite) will be created automatically on first run.

## Running the Platform

```bash
python platform_app.py
```

The platform will start on `http://localhost:5000`

## Login

Demo mode: Any username/password is accepted for login.

## Architecture

- `platform_app.py` - Main Flask application with all routes
- `hiresight_engine.py` - Wrapper around existing HireSight AI logic (black box)
- `database.py` - SQLite database for jobs, shortlists, notes, interviews
- `templates/` - Jinja2 templates for all pages
- `static/platform.css` - Modern CSS styling

## Notes

- The existing HireSight AI resume matching logic is preserved as-is
- All core search, embedding, and scoring functions remain unchanged
- The platform adds UI/UX and workflow management around the engine
- Original resume files are preserved in the `resumes/` folder
- Cleaned resumes are stored in `cleaned_resumes/` folder

## File Structure

```
.
├── platform_app.py          # Main Flask app
├── hiresight_engine.py      # HireSight engine wrapper
├── database.py              # Database schema and functions
├── templates/
│   ├── base.html            # Base template with sidebar
│   ├── login.html           # Login page
│   ├── dashboard.html       # Dashboard
│   ├── resume_repository.html
│   ├── resume_upload.html
│   ├── resume_search.html
│   ├── resume_notes.html
│   ├── jobs.html
│   ├── create_job.html
│   ├── view_job.html
│   ├── interviews.html
│   └── schedule_interview.html
└── static/
    └── platform.css         # Modern CSS
```
