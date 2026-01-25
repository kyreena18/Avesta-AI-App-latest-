"""
HireSight AI Platform - Recruiter ATS Platform
Main Flask application that builds a platform around the existing HireSight AI engine
"""

import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import hiresight_engine
import database

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.urandom(24).hex()  # For session management

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "resumes")
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
ORIGINAL_RESUMES_FOLDER = os.path.join(BASE_DIR, "resumes")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def require_login(f):
    """Decorator to require login"""
    def wrapper(*args, **kwargs):
        if 'recruiter_logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login - no real auth for demo"""
    if request.method == 'POST':
        # Simple demo login - accept any credentials
        session['recruiter_logged_in'] = True
        session['recruiter_name'] = request.form.get('username', 'Recruiter')
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user (demo mode - just creates session)"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        name = request.form.get('name', '').strip()
        # Demo mode: just create session
        session['recruiter_logged_in'] = True
        session['recruiter_name'] = name or email.split('@')[0] if email else 'Recruiter'
        flash('Registration successful!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.pop('recruiter_logged_in', None)
    session.pop('recruiter_name', None)
    return redirect(url_for('login'))


@app.route('/')
@require_login
def dashboard():
    """Dashboard landing page"""
    # Get statistics
    all_resumes = hiresight_engine.get_all_resumes()
    all_jobs = database.get_all_jobs()
    active_jobs = [j for j in all_jobs if j['status'] == 'active']
    shortlisted = database.get_shortlisted_resumes()
    
    return render_template('dashboard.html',
                         total_resumes=len(all_resumes),
                         total_jobs=len(all_jobs),
                         active_jobs=len(active_jobs),
                         shortlisted_count=len(shortlisted))


@app.route('/resumes')
@require_login
def resume_repository():
    """Resume Repository - Show all resumes"""
    resumes = hiresight_engine.get_all_resumes()
    # Add original file info
    for resume in resumes:
        original = hiresight_engine.find_original_resume(resume['id'])
        resume['original_file'] = original
        resume['has_file'] = original is not None
        # Get shortlist status
        shortlists = database.get_shortlisted_resumes()
        resume['is_shortlisted'] = any(s['resume_id'] == resume['id'] for s in shortlists)
    
    return render_template('resume_repository.html', resumes=resumes)


@app.route('/resumes/upload', methods=['GET', 'POST'])
@require_login
def resume_upload():
    """Resume Upload page"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Process and index the resume
            success = hiresight_engine.index_resume(filepath, filename)
            if success:
                flash(f'Resume "{filename}" uploaded and indexed successfully!', 'success')
            else:
                flash(f'Error processing resume "{filename}"', 'error')
            
            return redirect(url_for('resume_repository'))
        
        flash('Invalid file type. Please upload PDF or DOCX files.', 'error')
        return redirect(request.url)
    
    return render_template('resume_upload.html')


@app.route('/resumes/<resume_id>/download')
@require_login
def download_resume(resume_id):
    """Download original resume file"""
    original = hiresight_engine.find_original_resume(resume_id)
    if original and os.path.isfile(os.path.join(ORIGINAL_RESUMES_FOLDER, original)):
        return send_from_directory(ORIGINAL_RESUMES_FOLDER, original, as_attachment=True)
    flash('Resume file not found', 'error')
    return redirect(url_for('resume_repository'))


@app.route('/search', methods=['GET', 'POST'])
@require_login
def resume_search():
    """Resume Search page using HireSight logic"""
    results = []
    search_type = None
    query = ""
    
    if request.method == 'POST':
        search_type = request.form.get('search_type', 'jd')
        query = request.form.get('query', '')
        
        if search_type == 'jd':
            jd = request.form.get('jd', '').strip()
            if jd:
                results = hiresight_engine.search_by_jd(jd, top_k=10)
                query = jd
        
        elif search_type == 'skills':
            skills_str = request.form.get('skills', '').strip()
            years_str = request.form.get('years', '0').strip()
            skills = [s.strip() for s in skills_str.split(',') if s.strip()]
            try:
                min_years = int(years_str) if years_str else 0
            except:
                min_years = 0
            if skills:
                results = hiresight_engine.search_by_skills(skills, min_years, top_k=10)
                query = f"{skills_str} ({min_years} years)"
        
        elif search_type == 'education':
            levels_str = request.form.get('education', '').strip()
            levels = [l.strip() for l in levels_str.split(',') if l.strip()]
            if levels:
                results = hiresight_engine.search_by_education(levels, top_k=10)
                query = levels_str
        
        # Add original file info to results
        for result in results:
            original = hiresight_engine.find_original_resume(result['id'])
            result['original_file'] = original
            result['has_file'] = original is not None
    
    return render_template('resume_search.html', results=results, search_type=search_type, query=query)


@app.route('/jobs')
@require_login
def jobs():
    """Job Openings page"""
    all_jobs = database.get_all_jobs()
    # Add matched resume counts
    for job in all_jobs:
        # Count matched resumes (would need to run matching, simplified for now)
        job['matched_count'] = 0
    return render_template('jobs.html', jobs=all_jobs)


@app.route('/jobs/create', methods=['GET', 'POST'])
@require_login
def create_job():
    """Create new job opening"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        requirements = request.form.get('requirements', '').strip()
        skills = request.form.get('skills', '').strip()
        min_experience = request.form.get('min_experience', '0').strip()
        education_levels = request.form.get('education_levels', '').strip()
        
        try:
            min_experience = int(min_experience) if min_experience else 0
        except:
            min_experience = 0
        
        if title:
            job_id = database.create_job(title, description, requirements, skills, min_experience, education_levels)
            flash(f'Job "{title}" created successfully!', 'success')
            return redirect(url_for('view_job', job_id=job_id))
        else:
            flash('Job title is required', 'error')
    
    return render_template('create_job.html')


@app.route('/jobs/<int:job_id>/update-status', methods=['POST'])
@require_login
def update_job_status(job_id):
    """Update job status"""
    status = request.form.get('status', '').strip()
    if status:
        database.update_job_status(job_id, status)
        flash('Job status updated!', 'success')
    return redirect(url_for('jobs'))


@app.route('/jobs/<int:job_id>')
@require_login
def view_job(job_id):
    """View job and matched resumes"""
    job = database.get_job(job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('jobs'))
    
    # Run matching using HireSight engine
    matched_resumes = []
    if job['description']:
        matched_resumes = hiresight_engine.search_by_jd(job['description'], top_k=10)
    
    # Also try skills matching if available
    if job['skills']:
        skills = [s.strip() for s in job['skills'].split(',') if s.strip()]
        if skills:
            skill_matched = hiresight_engine.search_by_skills(skills, job.get('min_experience', 0), top_k=10)
            # Merge results, avoiding duplicates
            existing_ids = {r['id'] for r in matched_resumes}
            for r in skill_matched:
                if r['id'] not in existing_ids:
                    matched_resumes.append(r)
    
    # Add file info
    for resume in matched_resumes:
        original = hiresight_engine.find_original_resume(resume['id'])
        resume['original_file'] = original
        resume['has_file'] = original is not None
        # Check shortlist status
        shortlists = database.get_shortlisted_resumes(job_id)
        resume['is_shortlisted'] = any(s['resume_id'] == resume['id'] for s in shortlists)
        # Get notes
        resume['notes'] = database.get_notes(resume['id'], job_id)
    
    # Get shortlisted resumes for this job
    shortlisted = database.get_shortlisted_resumes(job_id)
    
    return render_template('view_job.html', job=job, matched_resumes=matched_resumes, shortlisted=shortlisted)


@app.route('/jobs/<int:job_id>/shortlist/<resume_id>', methods=['POST'])
@require_login
def shortlist_resume(job_id, resume_id):
    """Shortlist a resume for a job"""
    database.shortlist_resume(resume_id, job_id, 'shortlisted')
    flash('Resume shortlisted successfully!', 'success')
    return redirect(url_for('view_job', job_id=job_id))


@app.route('/jobs/<int:job_id>/reject/<resume_id>', methods=['POST'])
@require_login
def reject_resume(job_id, resume_id):
    """Reject a resume for a job"""
    database.shortlist_resume(resume_id, job_id, 'rejected')
    flash('Resume rejected', 'info')
    return redirect(url_for('view_job', job_id=job_id))


@app.route('/jobs/<int:job_id>/note/<resume_id>', methods=['POST'])
@require_login
def add_note(job_id, resume_id):
    """Add note to resume for a job"""
    note_text = request.form.get('note', '').strip()
    if note_text:
        database.add_note(resume_id, note_text, job_id)
        flash('Note added successfully!', 'success')
    return redirect(url_for('view_job', job_id=job_id))


@app.route('/resumes/<resume_id>/notes', methods=['GET', 'POST'])
@require_login
def resume_notes(resume_id):
    """View and manage notes for a resume"""
    if request.method == 'POST':
        note_text = request.form.get('note', '').strip()
        job_id = request.form.get('job_id', '').strip()
        job_id = int(job_id) if job_id and job_id.isdigit() else None
        if note_text:
            database.add_note(resume_id, note_text, job_id)
            flash('Note added successfully!', 'success')
            return redirect(url_for('resume_notes', resume_id=resume_id))
    
    notes = database.get_notes(resume_id)
    resume_name = hiresight_engine._display_name_from_id(resume_id)
    jobs = database.get_all_jobs()
    return render_template('resume_notes.html', resume_id=resume_id, resume_name=resume_name, notes=notes, jobs=jobs)


@app.route('/interviews')
@require_login
def interviews():
    """Interview Scheduler page"""
    all_interviews = database.get_interviews()
    # Add resume names
    for interview in all_interviews:
        interview['resume_name'] = hiresight_engine._display_name_from_id(interview['resume_id'])
        job = database.get_job(interview.get('job_id')) if interview.get('job_id') else None
        interview['job_title'] = job['title'] if job else 'General'
    return render_template('interviews.html', interviews=all_interviews)


@app.route('/interviews/schedule', methods=['GET', 'POST'])
@require_login
def schedule_interview():
    """Schedule an interview"""
    if request.method == 'POST':
        resume_id = request.form.get('resume_id', '').strip()
        job_id = request.form.get('job_id', '').strip()
        scheduled_date = request.form.get('scheduled_date', '').strip()
        interview_type = request.form.get('interview_type', 'phone').strip()
        notes = request.form.get('notes', '').strip()
        
        job_id = int(job_id) if job_id and job_id.isdigit() else None
        
        if resume_id and scheduled_date:
            interview_id = database.schedule_interview(resume_id, scheduled_date, job_id, interview_type, notes)
            flash('Interview scheduled successfully!', 'success')
            return redirect(url_for('interviews'))
        else:
            flash('Resume ID and scheduled date are required', 'error')
    
    # Get resumes and jobs for dropdown
    resumes = hiresight_engine.get_all_resumes()
    jobs = database.get_all_jobs(status='active')
    return render_template('schedule_interview.html', resumes=resumes, jobs=jobs)


@app.route('/interviews/<int:interview_id>/update-status', methods=['POST'])
@require_login
def update_interview_status(interview_id):
    """Update interview status"""
    status = request.form.get('status', '').strip()
    if status:
        database.update_interview_status(interview_id, status)
        flash('Interview status updated!', 'success')
    return redirect(url_for('interviews'))


@app.route('/resume/<path:filename>')
@require_login
def serve_resume(filename):
    """Serve resume file"""
    safe_path = os.path.join(ORIGINAL_RESUMES_FOLDER, filename)
    if os.path.isfile(safe_path):
        return send_from_directory(ORIGINAL_RESUMES_FOLDER, os.path.basename(safe_path), as_attachment=False)
    return ("File not found", 404)


if __name__ == '__main__':
    # Initialize database
    database.init_db()
    # Initialize HireSight engine index
    hiresight_engine.index_if_needed()
    app.run(host="0.0.0.0", port=5000, debug=True)
