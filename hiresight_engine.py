"""
HireSight AI Engine - Core Resume Matching Logic
This module wraps the existing HireSight AI resume matching functionality
as a black box that the platform can use.
"""

import os
import re
from typing import List, Tuple, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer
import PyPDF2
import docx

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLEANED_FOLDER = os.path.join(BASE_DIR, "cleaned_resumes")
INTERVIEW_FOLDER = os.path.join(BASE_DIR, "interview_notes")
ORIGINAL_RESUMES_FOLDER = os.path.join(BASE_DIR, "resumes")
CHROMA_PATH = os.path.join(BASE_DIR, "resume_db")

# Initialize embedding model and ChromaDB
_model = None
_chroma_client = None
_collection = None


def _get_model():
    """Lazy load the embedding model"""
    global _model
    if _model is None:
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model


def _get_collection():
    """Lazy load ChromaDB collection"""
    global _chroma_client, _collection
    if _collection is None:
        _chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _chroma_client.get_or_create_collection("resumes")
    return _collection


def embed_text(text: str) -> List[float]:
    """Embed text using the sentence transformer model"""
    model = _get_model()
    return model.encode([text], normalize_embeddings=True)[0].tolist()


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    text = ""
    doc = docx.Document(file_path)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


def clean_resume_text(text: str) -> str:
    """Clean resume text (basic cleaning)"""
    text = re.sub(r'\s+', ' ', text)  # remove extra spaces/newlines
    text = re.sub(r'[^\w\s.,]', '', text)  # keep only words, numbers, punctuation
    return text.strip()


def load_documents() -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
    """Load all documents from cleaned_resumes and interview_notes folders"""
    docs, ids, metadatas = [], [], []
    for folder in [CLEANED_FOLDER, INTERVIEW_FOLDER]:
        if not os.path.exists(folder):
            continue
        doc_type = "resume" if folder == CLEANED_FOLDER else "note"
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            if os.path.isfile(fpath) and fname.endswith('.txt'):
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                if text:
                    docs.append(text)
                    ids.append(fname)
                    metadatas.append({"type": doc_type, "filename": fname})
    return docs, ids, metadatas


def index_if_needed():
    """Index documents if collection is empty"""
    collection = _get_collection()
    existing = collection.get()
    if len(existing.get("ids", [])) == 0:
        docs, ids, metadatas = load_documents()
        for i, doc in enumerate(docs):
            emb = embed_text(doc)
            collection.add(
                documents=[doc], embeddings=[emb], ids=[ids[i]], metadatas=[metadatas[i]]
            )
        return True
    return False


def index_resume(file_path: str, resume_id: str) -> bool:
    """
    Process and index a new resume file.
    Returns True if successful, False otherwise.
    """
    try:
        # Extract text
        if file_path.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            text = extract_text_from_docx(file_path)
        else:
            return False
        
        # Clean text
        cleaned_text = clean_resume_text(text)
        if not cleaned_text:
            return False
        
        # Save cleaned text
        os.makedirs(CLEANED_FOLDER, exist_ok=True)
        cleaned_filename = os.path.basename(file_path).rsplit('.', 1)[0] + '_cleaned.txt'
        cleaned_filepath = os.path.join(CLEANED_FOLDER, cleaned_filename)
        with open(cleaned_filepath, "w", encoding="utf-8") as f:
            f.write(cleaned_text)
        
        # Embed and add to ChromaDB
        collection = _get_collection()
        emb = embed_text(cleaned_text)
        collection.add(
            documents=[cleaned_text],
            embeddings=[emb],
            ids=[cleaned_filename],
            metadatas=[{"type": "resume", "filename": cleaned_filename}]
        )
        
        return True
    except Exception as e:
        print(f"Error indexing resume: {e}")
        return False


def search_profiles(query: str, top_k: int = 5, include_notes: bool = False) -> List[Tuple[str, str, float, Dict[str, Any]]]:
    """Search for profiles matching the query"""
    collection = _get_collection()
    query_emb = embed_text(query)
    where = None if include_notes else {"type": "resume"}
    results = collection.query(query_embeddings=[query_emb], n_results=top_k, where=where)
    return list(
        zip(
            results.get("ids", [["-"]])[0],
            results.get("documents", [[""]])[0],
            results.get("distances", [[0.0]])[0],
            results.get("metadatas", [[{}]])[0],
        )
    )


def score_skills_and_experience(text: str, required_skills: List[str], min_years: int) -> float:
    """Score resume based on skills and experience"""
    text_lower = text.lower()
    score = 0.0
    for skill in required_skills:
        if skill.lower() in text_lower:
            score += 1.0
    years = 0
    YEARS_PATTERN = re.compile(r"(\d+)\s*(?:\+?\s*)?(?:years|yrs|year)\b", re.IGNORECASE)
    for m in YEARS_PATTERN.finditer(text_lower):
        try:
            years = max(years, int(m.group(1)))
        except ValueError:
            continue
    if years >= min_years:
        score += 0.5
    return score


def score_education(text: str, levels: List[str]) -> float:
    """Score resume based on education level"""
    text_lower = text.lower()
    score = 0.0
    keywords = {
        "phd": ["phd", "doctor of philosophy"],
        "masters": ["masters", "m.s.", "ms ", "m.tech", "mtech", "m.sc", "msc"],
        "bachelors": ["bachelors", "b.e.", "btech", "b.tech", "b.sc", "bsc", "bca", "b.eng"],
    }
    for level in levels:
        for kw in keywords.get(level.lower(), []):
            if kw in text_lower:
                score += 1.0
                break
    return score


def search_by_jd(jd: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Search resumes by job description"""
    results = search_profiles(jd, top_k=top_k, include_notes=False)
    payload = []
    for rid, doc, dist, meta in results:
        preview = " ".join(doc.split()[:50]) + "..."
        payload.append({
            "id": rid,
            "name": _display_name_from_id(rid),
            "similarity": round(1 - float(dist), 4),
            "preview": preview,
            "type": meta.get("type") if isinstance(meta, dict) else None,
            "full_text": doc,
        })
    return payload


def search_by_skills(skills: List[str], min_years: int = 0, top_k: int = 10) -> List[Dict[str, Any]]:
    """Search resumes by skills and experience"""
    semantic_query = ", ".join(skills) + (f", {min_years} years" if min_years else "")
    candidates = search_profiles(semantic_query, top_k=top_k, include_notes=False)
    rescored = []
    for rid, doc, dist, meta in candidates:
        skill_score = score_skills_and_experience(doc, skills, min_years)
        combined = (1 - dist) + 0.3 * skill_score
        rescored.append((combined, rid, doc, dist, meta))
    rescored.sort(reverse=True)
    
    payload = []
    for combined, rid, doc, dist, meta in rescored[:top_k]:
        preview = " ".join(doc.split()[:50]) + "..."
        payload.append({
            "id": rid,
            "name": _display_name_from_id(rid),
            "score": round(float(combined), 4),
            "similarity": round(1 - float(dist), 4),
            "preview": preview,
            "type": meta.get("type") if isinstance(meta, dict) else None,
            "full_text": doc,
        })
    return payload


def search_by_education(levels: List[str], top_k: int = 10) -> List[Dict[str, Any]]:
    """Search resumes by education level"""
    semantic_query = "candidates with " + ", ".join(levels)
    candidates = search_profiles(semantic_query, top_k=top_k, include_notes=False)
    rescored = []
    for rid, doc, dist, meta in candidates:
        edu_score = score_education(doc, levels)
        combined = (1 - dist) + 0.4 * edu_score
        rescored.append((combined, rid, doc, dist, meta))
    rescored.sort(reverse=True)
    
    payload = []
    for combined, rid, doc, dist, meta in rescored[:top_k]:
        preview = " ".join(doc.split()[:50]) + "..."
        payload.append({
            "id": rid,
            "name": _display_name_from_id(rid),
            "score": round(float(combined), 4),
            "similarity": round(1 - float(dist), 4),
            "preview": preview,
            "type": meta.get("type") if isinstance(meta, dict) else None,
            "full_text": doc,
        })
    return payload


def get_all_resumes() -> List[Dict[str, Any]]:
    """Get all indexed resumes"""
    collection = _get_collection()
    results = collection.get(where={"type": "resume"})
    resumes = []
    for i, resume_id in enumerate(results.get("ids", [])):
        metadata = results.get("metadatas", [{}])[i] if i < len(results.get("metadatas", [])) else {}
        resumes.append({
            "id": resume_id,
            "name": _display_name_from_id(resume_id),
            "filename": metadata.get("filename", resume_id),
        })
    return resumes


def _display_name_from_id(file_id: str) -> str:
    """Extract display name from file ID"""
    stem = os.path.splitext(file_id)[0]
    parts = stem.split("_")
    return parts[0].strip() if parts else stem.strip()


def find_original_resume(cleaned_id: str) -> Optional[str]:
    """Find original resume file from cleaned ID"""
    if not os.path.isdir(ORIGINAL_RESUMES_FOLDER):
        return None
    
    def _strip_cleaned_suffix(name: str) -> str:
        base = os.path.splitext(name)[0]
        base = re.sub(r"(?i)_hiresight_cleaned$", "_HireSight", base)
        base = re.sub(r"(?i)_cleaned$", "", base)
        return base
    
    preferred_bases = [
        _strip_cleaned_suffix(cleaned_id),
        re.sub(r"(?i)_hiresight_cleaned$", "", os.path.splitext(cleaned_id)[0]),
        os.path.splitext(cleaned_id)[0]
    ]
    
    originals = [f for f in os.listdir(ORIGINAL_RESUMES_FOLDER) 
                 if os.path.isfile(os.path.join(ORIGINAL_RESUMES_FOLDER, f))]
    originals_lower = [f.lower() for f in originals]
    
    for base in preferred_bases:
        for ext in (".pdf", ".docx"):
            candidate = base + ext
            if candidate in originals or candidate.lower() in originals_lower:
                if candidate in originals:
                    return candidate
                return originals[originals_lower.index(candidate.lower())]
    
    for base in preferred_bases:
        base_lower = base.lower()
        for orig, orig_l in zip(originals, originals_lower):
            stem = os.path.splitext(orig_l)[0]
            if stem.startswith(base_lower) and (orig_l.endswith('.pdf') or orig_l.endswith('.docx')):
                return orig
    return None


# Initialize on import
index_if_needed()
