"""
Database module for HireSight Platform using Supabase
Handles jobs, shortlists, notes, interviews, and authentication
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from supabase_config import supabase
from flask import session as flask_session


def create_job(title: str, description: str = "", requirements: str = "", 
               skills: str = "", min_experience: int = 0, education_levels: str = "") -> int:
    """Create a new job opening"""
    result = supabase.table("jobs").insert({
        "title": title,
        "description": description,
        "requirements": requirements,
        "skills": skills,
        "min_experience": min_experience,
        "education_levels": education_levels,
        "status": "active"
    }).execute()
    
    return result.data[0]["id"]


def get_job(job_id: int) -> Optional[Dict[str, Any]]:
    """Get job by ID"""
    result = supabase.table("jobs").select("*").eq("id", job_id).execute()
    return result.data[0] if result.data else None


def get_all_jobs(status: str = None) -> List[Dict[str, Any]]:
    """Get all jobs, optionally filtered by status"""
    query = supabase.table("jobs").select("*").order("created_at", desc=True)
    if status:
        query = query.eq("status", status)
    result = query.execute()
    return result.data


def update_job_status(job_id: int, status: str):
    """Update job status"""
    supabase.table("jobs").update({"status": status}).eq("id", job_id).execute()


def shortlist_resume(resume_id: str, job_id: Optional[int] = None, status: str = 'shortlisted'):
    """Shortlist a resume"""
    # Check if already exists
    existing = supabase.table("shortlists").select("*").eq("resume_id", resume_id).eq("job_id", job_id).execute()
    
    if existing.data:
        supabase.table("shortlists").update({"status": status}).eq("resume_id", resume_id).eq("job_id", job_id).execute()
    else:
        supabase.table("shortlists").insert({
            "resume_id": resume_id,
            "job_id": job_id,
            "status": status
        }).execute()


def get_shortlisted_resumes(job_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get shortlisted resumes, optionally filtered by job"""
    query = supabase.table("shortlists").select("*").order("created_at", desc=True)
    if job_id:
        query = query.eq("job_id", job_id)
    result = query.execute()
    return result.data


def add_note(resume_id: str, note_text: str, job_id: Optional[int] = None) -> int:
    """Add a note to a resume"""
    result = supabase.table("notes").insert({
        "resume_id": resume_id,
        "job_id": job_id,
        "note_text": note_text
    }).execute()
    return result.data[0]["id"]


def get_notes(resume_id: str, job_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get notes for a resume"""
    query = supabase.table("notes").select("*").eq("resume_id", resume_id).order("created_at", desc=True)
    if job_id:
        query = query.eq("job_id", job_id)
    result = query.execute()
    return result.data


def schedule_interview(resume_id: str, scheduled_date: str, job_id: Optional[int] = None,
                      interview_type: str = 'phone', notes: str = "") -> int:
    """Schedule an interview"""
    result = supabase.table("interviews").insert({
        "resume_id": resume_id,
        "job_id": job_id,
        "scheduled_date": scheduled_date,
        "interview_type": interview_type,
        "status": "scheduled",
        "notes": notes
    }).execute()
    return result.data[0]["id"]


def get_interviews(resume_id: Optional[str] = None, job_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get interviews, optionally filtered"""
    query = supabase.table("interviews").select("*").order("scheduled_date", desc=False)
    if resume_id and job_id:
        query = query.eq("resume_id", resume_id).eq("job_id", job_id)
    elif resume_id:
        query = query.eq("resume_id", resume_id)
    elif job_id:
        query = query.eq("job_id", job_id)
    result = query.execute()
    return result.data


def update_interview_status(interview_id: int, status: str):
    """Update interview status"""
    supabase.table("interviews").update({"status": status}).eq("id", interview_id).execute()


# Authentication functions
def create_user(email: str, password: str, name: str = "") -> Dict[str, Any]:
    """Create a new user account"""
    try:
        result = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "name": name
                }
            }
        })
        
        # Check if user was created successfully
        if not result:
            raise Exception("No response from Supabase")
        
        if not result.user:
            # Try to get error message from result
            error_msg = "Failed to create user account"
            if hasattr(result, 'message'):
                error_msg = result.message
            raise Exception(error_msg)
        
        # Store session if user is created and session is available
        # Note: If email confirmation is enabled, session might be None
        if result.session:
            flask_session['supabase_access_token'] = result.session.access_token
            flask_session['supabase_refresh_token'] = result.session.refresh_token
            # Set the session on the Supabase client
            supabase.auth.set_session(
                access_token=result.session.access_token,
                refresh_token=result.session.refresh_token
            )
        
        return result
    except Exception as e:
        # Re-raise with more context
        error_msg = str(e)
        error_lower = error_msg.lower()
        
        # Handle Supabase-specific errors
        if "already registered" in error_lower or "user already exists" in error_lower or "already been registered" in error_lower:
            raise Exception("User already registered")
        elif "invalid" in error_lower and "email" in error_lower:
            raise Exception("Invalid email address")
        elif "password" in error_lower and ("weak" in error_lower or "short" in error_lower or "minimum" in error_lower):
            raise Exception("Password does not meet requirements (minimum 6 characters)")
        elif "email" in error_lower and ("format" in error_lower or "invalid" in error_lower):
            raise Exception("Invalid email address format")
        else:
            # Return the original error message for debugging
            raise Exception(f"Registration failed: {error_msg}")


def sign_in(email: str, password: str) -> Dict[str, Any]:
    """Sign in a user"""
    try:
        result = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        # Check if sign in was successful
        if not result:
            raise Exception("No response from Supabase")
        
        if not result.user:
            # Try to get error message from result
            error_msg = "Invalid login credentials"
            if hasattr(result, 'message'):
                error_msg = result.message
            raise Exception(error_msg)
        
        # Store session tokens in Flask session
        if result.session:
            flask_session['supabase_access_token'] = result.session.access_token
            flask_session['supabase_refresh_token'] = result.session.refresh_token
            # Set the session on the Supabase client
            supabase.auth.set_session(
                access_token=result.session.access_token,
                refresh_token=result.session.refresh_token
            )
        else:
            raise Exception("Session not available. Please check if email confirmation is required.")
        
        return result
    except Exception as e:
        error_msg = str(e)
        error_lower = error_msg.lower()
        
        # Handle Supabase-specific errors
        if "invalid" in error_lower and ("credentials" in error_lower or "password" in error_lower or "login" in error_lower):
            raise Exception("Invalid email or password")
        elif "email not confirmed" in error_lower or "email_not_confirmed" in error_lower or "not confirmed" in error_lower:
            raise Exception("Please confirm your email before logging in")
        elif "user not found" in error_lower or "does not exist" in error_lower:
            raise Exception("No account found with this email. Please register first.")
        else:
            raise Exception(f"Login failed: {error_msg}")


def get_current_user():
    """Get the current authenticated user"""
    # Restore session from Flask session if available
    access_token = flask_session.get('supabase_access_token')
    refresh_token = flask_session.get('supabase_refresh_token')
    
    if access_token and refresh_token:
        try:
            # Set the session on the Supabase client
            supabase.auth.set_session(
                access_token=access_token,
                refresh_token=refresh_token
            )
            # Get the user
            return supabase.auth.get_user()
        except Exception:
            # Session might be expired, clear it
            flask_session.pop('supabase_access_token', None)
            flask_session.pop('supabase_refresh_token', None)
            return None
    
    # Try to get user without session (might work if session is still valid in client)
    try:
        return supabase.auth.get_user()
    except Exception:
        return None


def sign_out():
    """Sign out the current user"""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    finally:
        # Clear session tokens from Flask session
        flask_session.pop('supabase_access_token', None)
        flask_session.pop('supabase_refresh_token', None)
