"""
HireSight Platform - Recruiter ATS Platform with Supabase
Main Flask application with Supabase integration for database and authentication
"""

import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, flash
from werkzeug.utils import secure_filename
from datetime import datetime
import hiresight_engine
import database_supabase as database
from supabase_config import supabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.urandom(24).hex()  # For session management

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "resumes")
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
ORIGINAL_RESUMES_FOLDER = os.path.join(BASE_DIR, "resumes")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.before_request
def restore_supabase_session():
    """Restore Supabase session from Flask session on each request"""
    access_token = session.get('supabase_access_token')
    refresh_token = session.get('supabase_refresh_token')
    
    if access_token and refresh_token:
        try:
            supabase.auth.set_session(
                access_token=access_token,
                refresh_token=refresh_token
            )
        except Exception:
            # Session might be invalid, clear it
            session.pop('supabase_access_token', None)
            session.pop('supabase_refresh_token', None)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def require_login(f):
    """Decorator to require login"""
    def wrapper(*args, **kwargs):
        # Check if user is authenticated in Supabase
        try:
            user = database.get_current_user()
            if not user or not user.user:
                # Clear any stale session data
                session.pop('user_id', None)
                session.pop('user_email', None)
                session.pop('user_name', None)
                session.pop('supabase_access_token', None)
                session.pop('supabase_refresh_token', None)
                flash('Please login to continue', 'error')
                return redirect(url_for('login'))
            # Update session with current user info
            session['user_id'] = user.user.id
            session['user_email'] = user.user.email
            if not session.get('user_name'):
                session['user_name'] = user.user.user_metadata.get('name', user.user.email.split('@')[0])
        except Exception as e:
            # If authentication fails, redirect to login
            session.pop('user_id', None)
            session.pop('user_email', None)
            session.pop('user_name', None)
            session.pop('supabase_access_token', None)
            session.pop('supabase_refresh_token', None)
            flash('Please login to continue', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login using Supabase authentication"""
    # Redirect if already logged in
    if 'user_id' in session:
        try:
            user = database.get_current_user()
            if user:
                return redirect(url_for('dashboard'))
        except:
            pass
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        
        # Basic validation
        if not email:
            flash('Email is required', 'error')
            return render_template('login.html')
        
        if not password:
            flash('Password is required', 'error')
            return render_template('login.html')
        
        # Validate email format
        if '@' not in email or '.' not in email.split('@')[1]:
            flash('Please enter a valid email address', 'error')
            return render_template('login.html')
        
        try:
            logger.info(f"Attempting to login user: {email}")
            result = database.sign_in(email, password)
            logger.info(f"Login result: user={result.user if result else None}, session={result.session if result else None}")
            
            if result and result.user:
                session['user_id'] = result.user.id
                session['user_email'] = result.user.email
                session['user_name'] = result.user.user_metadata.get('name', email.split('@')[0])
                logger.info(f"User logged in successfully: {result.user.id}")
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                logger.error("Login failed: No user returned")
                flash('Login failed: Invalid credentials', 'error')
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Login error: {error_msg}", exc_info=True)
            # Make error messages more user-friendly
            if 'invalid' in error_msg.lower() and ('credentials' in error_msg.lower() or 'password' in error_msg.lower()):
                flash('Invalid email or password. Please check your credentials.', 'error')
            elif 'email not confirmed' in error_msg.lower() or 'email_not_confirmed' in error_msg.lower():
                flash('Please confirm your email address before logging in. Check your inbox for the confirmation email.', 'error')
            else:
                flash(f'Login failed: {error_msg}', 'error')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user"""
    # Redirect if already logged in
    if 'user_id' in session:
        try:
            user = database.get_current_user()
            if user:
                return redirect(url_for('dashboard'))
        except:
            pass
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        name = request.form.get('name', '').strip()
        
        # Basic validation
        if not email:
            flash('Email is required', 'error')
            return render_template('register.html')
        
        if not password:
            flash('Password is required', 'error')
            return render_template('register.html')
        
        # Validate email format
        if '@' not in email or '.' not in email.split('@')[1]:
            flash('Please enter a valid email address', 'error')
            return render_template('register.html')
        
        # Validate password length
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')
        
        try:
            logger.info(f"Attempting to register user: {email}")
            result = database.create_user(email, password, name)
            logger.info(f"Registration result: user={result.user if result else None}, session={result.session if result else None}")
            
            if result and result.user:
                # Check if email confirmation is required
                if result.session:
                    # User is automatically logged in
                    session['user_id'] = result.user.id
                    session['user_email'] = result.user.email
                    session['user_name'] = result.user.user_metadata.get('name', name or email.split('@')[0])
                    logger.info(f"User registered and logged in: {result.user.id}")
                    flash('Registration successful! You are now logged in.', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    # Email confirmation required
                    logger.info(f"User registered but email confirmation required: {result.user.id}")
                    flash('Registration successful! Please check your email to confirm your account before logging in.', 'success')
                    return redirect(url_for('login'))
            else:
                logger.error("Registration failed: No user returned")
                flash('Registration failed: Please try again', 'error')
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Registration error: {error_msg}", exc_info=True)
            # Make error messages more user-friendly
            if 'already registered' in error_msg.lower() or 'user already exists' in error_msg.lower():
                flash('This email is already registered. Please login instead.', 'error')
            elif 'invalid email' in error_msg.lower():
                flash('Please enter a valid email address', 'error')
            elif 'password' in error_msg.lower():
                flash('Password does not meet requirements. Please use at least 6 characters.', 'error')
            else:
                flash(f'Registration failed: {error_msg}', 'error')
    
    return render_template('register.html')


@app.route('/logout')
def logout():
    """Logout"""
    database.sign_out()
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_name', None)
    flash('Logged out successfully', 'info')
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
    # Initialize HireSight engine index
    hiresight_engine.index_if_needed()
    app.run(host="0.0.0.0", port=5000, debug=True)
