"""
Database module for HireSight Platform
Handles jobs, shortlists, notes, and interviews
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "hiresight_platform.db")


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Jobs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            requirements TEXT,
            skills TEXT,
            min_experience INTEGER DEFAULT 0,
            education_levels TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Shortlists table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shortlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id TEXT NOT NULL,
            job_id INTEGER,
            status TEXT DEFAULT 'shortlisted',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)
    
    # Notes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id TEXT NOT NULL,
            job_id INTEGER,
            note_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)
    
    # Interviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id TEXT NOT NULL,
            job_id INTEGER,
            scheduled_date TIMESTAMP,
            interview_type TEXT DEFAULT 'phone',
            status TEXT DEFAULT 'scheduled',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id)
        )
    """)
    
    conn.commit()
    conn.close()


def create_job(title: str, description: str = "", requirements: str = "", 
               skills: str = "", min_experience: int = 0, education_levels: str = "") -> int:
    """Create a new job opening"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs (title, description, requirements, skills, min_experience, education_levels)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, description, requirements, skills, min_experience, education_levels))
    job_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return job_id


def get_job(job_id: int) -> Optional[Dict[str, Any]]:
    """Get job by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def get_all_jobs(status: str = None) -> List[Dict[str, Any]]:
    """Get all jobs, optionally filtered by status"""
    conn = get_db()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM jobs WHERE status = ? ORDER BY created_at DESC", (status,))
    else:
        cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_job_status(job_id: int, status: str):
    """Update job status"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", 
                   (status, job_id))
    conn.commit()
    conn.close()


def shortlist_resume(resume_id: str, job_id: Optional[int] = None, status: str = 'shortlisted'):
    """Shortlist a resume"""
    conn = get_db()
    cursor = conn.cursor()
    # Check if already shortlisted
    cursor.execute("SELECT id FROM shortlists WHERE resume_id = ? AND job_id = ?", 
                   (resume_id, job_id))
    if cursor.fetchone():
        cursor.execute("UPDATE shortlists SET status = ? WHERE resume_id = ? AND job_id = ?",
                       (status, resume_id, job_id))
    else:
        cursor.execute("INSERT INTO shortlists (resume_id, job_id, status) VALUES (?, ?, ?)",
                       (resume_id, job_id, status))
    conn.commit()
    conn.close()


def get_shortlisted_resumes(job_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get shortlisted resumes, optionally filtered by job"""
    conn = get_db()
    cursor = conn.cursor()
    if job_id:
        cursor.execute("SELECT * FROM shortlists WHERE job_id = ? ORDER BY created_at DESC", (job_id,))
    else:
        cursor.execute("SELECT * FROM shortlists ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_note(resume_id: str, note_text: str, job_id: Optional[int] = None) -> int:
    """Add a note to a resume"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notes (resume_id, job_id, note_text) VALUES (?, ?, ?)",
                   (resume_id, job_id, note_text))
    note_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return note_id


def get_notes(resume_id: str, job_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get notes for a resume"""
    conn = get_db()
    cursor = conn.cursor()
    if job_id:
        cursor.execute("SELECT * FROM notes WHERE resume_id = ? AND job_id = ? ORDER BY created_at DESC",
                       (resume_id, job_id))
    else:
        cursor.execute("SELECT * FROM notes WHERE resume_id = ? ORDER BY created_at DESC", (resume_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def schedule_interview(resume_id: str, scheduled_date: str, job_id: Optional[int] = None,
                      interview_type: str = 'phone', notes: str = "") -> int:
    """Schedule an interview"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interviews (resume_id, job_id, scheduled_date, interview_type, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (resume_id, job_id, scheduled_date, interview_type, notes))
    interview_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return interview_id


def get_interviews(resume_id: Optional[str] = None, job_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get interviews, optionally filtered"""
    conn = get_db()
    cursor = conn.cursor()
    if resume_id and job_id:
        cursor.execute("SELECT * FROM interviews WHERE resume_id = ? AND job_id = ? ORDER BY scheduled_date",
                       (resume_id, job_id))
    elif resume_id:
        cursor.execute("SELECT * FROM interviews WHERE resume_id = ? ORDER BY scheduled_date", (resume_id,))
    elif job_id:
        cursor.execute("SELECT * FROM interviews WHERE job_id = ? ORDER BY scheduled_date", (job_id,))
    else:
        cursor.execute("SELECT * FROM interviews ORDER BY scheduled_date")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_interview_status(interview_id: int, status: str):
    """Update interview status"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE interviews SET status = ? WHERE id = ?", (status, interview_id))
    conn.commit()
    conn.close()


# Initialize database on import
init_db()
