#!/usr/bin/env python3
"""
Enhanced Web App with Fixed Education Matching
This addresses the indexing and search issues found in the diagnostic
"""

import os
import re
from typing import List, Tuple, Dict, Any
from flask import Flask, render_template, request, send_from_directory, jsonify
import chromadb
from sentence_transformers import SentenceTransformer

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLEANED_FOLDER = os.path.join(BASE_DIR, "cleaned_resumes")
INTERVIEW_FOLDER = os.path.join(BASE_DIR, "interview_notes")
ORIGINAL_RESUMES_FOLDER = os.path.join(BASE_DIR, "resumes")
CHROMA_PATH = os.path.join(BASE_DIR, "resume_db")

# Embedding model and DB
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection("resumes")

app = Flask(__name__, template_folder="templates", static_folder="static")

def embed_text(text: str) -> List[float]:
    return model.encode([text], normalize_embeddings=True)[0].tolist()

def load_documents() -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
    docs, ids, metadatas = [], [], []
    for folder in [CLEANED_FOLDER, INTERVIEW_FOLDER]:
        if not os.path.exists(folder):
            continue
        doc_type = "resume" if folder == CLEANED_FOLDER else "note"
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            if os.path.isfile(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read().strip()
                if text:
                    docs.append(text)
                    ids.append(fname)
                    metadatas.append({"type": doc_type, "filename": fname})
    return docs, ids, metadatas

def index_if_needed():
    existing = collection.get()
    if len(existing.get("ids", [])) == 0:
        docs, ids, metadatas = load_documents()
        for i, doc in enumerate(docs):
            emb = embed_text(doc)
            collection.add(
                documents=[doc], embeddings=[emb], ids=[ids[i]], metadatas=[metadatas[i]]
            )

def search_profiles(query: str, top_k: int = 5, include_notes: bool = True):
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

# Enhanced education matching with context awareness
class EnhancedEducationMatcher:
    def __init__(self):
        # More precise patterns with word boundaries
        self.education_patterns = {
            'phd': [
                r'\b(?:ph\.?d\.?|doctor of philosophy|doctorate|doctoral|d\.phil|dphil)\b',
                r'\b(?:phd|ph\.d|ph\.d\.|doctor of philosophy|doctorate|doctoral|d\.phil|dphil)\b'
            ],
            'masters': [
                r'\b(?:m\.?s\.?|m\.?tech|mtech|m\.?sc|msc|master of|mba|m\.?e\.?|me|mca|m\.?com|mcom|m\.?a\.?|ma|master\'s|master degree)\b',
                r'\b(?:m\.s\.|ms|m\.tech|mtech|m\.sc|msc|master of|mba|m\.e\.|me|mca|m\.com|mcom|m\.a\.|ma|master\'s|master degree)\b'
            ],
            'bachelors': [
                r'\b(?:b\.?e\.?|btech|b\.?tech|b\.?sc|bsc|bca|b\.?eng|bachelor of|bachelor\'s|b\.?com|bcom|b\.?a\.?|ba|bachelor degree|bachelor of technology|bachelor of engineering)\b',
                r'\b(?:b\.e\.|btech|b\.tech|b\.sc|bsc|bca|b\.eng|bachelor of|bachelor\'s|b\.com|bcom|b\.a\.|ba|bachelor degree|bachelor of technology|bachelor of engineering)\b'
            ]
        }
        
        # Education hierarchy (higher number = higher education)
        self.education_hierarchy = {
            'bachelors': 1,
            'masters': 2, 
            'phd': 3
        }
    
    def extract_education_section(self, text: str) -> str:
        """Extract education section with better context detection"""
        lines = text.split('\n')
        education_lines = []
        in_education = False
        education_keywords = ['education', 'qualification', 'degree', 'academic', 'university', 'college', 'institute', 'school']
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if we're entering education section
            if any(keyword in line_lower for keyword in education_keywords):
                in_education = True
                education_lines.append(line)
                continue
            
            # If we're in education section, collect lines
            if in_education:
                # Stop if we hit another major section
                if any(section in line_lower for section in ['experience', 'work history', 'professional experience', 'skills', 'projects', 'certification', 'achievements']):
                    break
                education_lines.append(line)
        
        return '\n'.join(education_lines)
    
    def find_education_matches(self, text: str, target_levels: List[str] = None) -> List[Dict[str, Any]]:
        """Find education matches with context awareness"""
        text_lower = text.lower()
        education_section = self.extract_education_section(text)
        education_section_lower = education_section.lower()
        
        matches = []
        levels_to_check = target_levels if target_levels else ['phd', 'masters', 'bachelors']
        
        for level in levels_to_check:
            if level not in self.education_patterns:
                continue
                
            keywords_found = []
            for pattern in self.education_patterns[level]:
                pattern_matches = re.findall(pattern, text_lower)
                if pattern_matches:
                    keywords_found.extend(pattern_matches)
            
            if keywords_found:
                # Calculate confidence based on context
                confidence = self.calculate_confidence(keywords_found, education_section_lower, level)
                
                matches.append({
                    'level': level,
                    'confidence': confidence,
                    'context': education_section,
                    'keywords_found': keywords_found
                })
        
        return matches
    
    def calculate_confidence(self, keywords_found: List[str], education_section: str, level: str) -> float:
        """Calculate confidence score for education match"""
        base_confidence = 0.5
        
        # Higher confidence if found in education section
        if any(keyword in education_section for keyword in keywords_found):
            base_confidence += 0.3
        
        # Higher confidence for more specific keywords
        specific_keywords = ['phd', 'doctorate', 'masters', 'mba', 'btech', 'bachelor']
        if any(keyword in keywords_found for keyword in specific_keywords):
            base_confidence += 0.2
        
        # Penalize if found in non-education context
        if 'experience' in education_section or 'work' in education_section:
            base_confidence -= 0.1
        
        return min(1.0, max(0.0, base_confidence))
    
    def get_highest_education(self, text: str, target_levels: List[str] = None) -> Dict[str, Any]:
        """Get the highest education level found, resolving conflicts"""
        matches = self.find_education_matches(text, target_levels)
        
        if not matches:
            return None
        
        # If multiple levels found, prioritize the highest
        if len(matches) > 1:
            # Sort by education hierarchy (PhD > Masters > Bachelors)
            matches.sort(key=lambda x: self.education_hierarchy.get(x['level'], 0), reverse=True)
            
            # Return the highest level with good confidence
            for match in matches:
                if match['confidence'] > 0.6:
                    return match
            
            # If no high confidence match, return the highest level
            return matches[0]
        
        return matches[0]
    
    def strict_education_filter(self, text: str, target_levels: List[str]) -> bool:
        """Strict filtering that only returns True for exact matches"""
        highest_education = self.get_highest_education(text, target_levels)
        
        if not highest_education:
            return False
        
        # Only return True if the highest education matches one of the target levels
        return highest_education['level'] in [level.lower() for level in target_levels]
    
    def get_education_keywords_found(self, text: str, target_levels: List[str]) -> List[str]:
        """Get the specific education keywords found for highlighting"""
        highest_education = self.get_highest_education(text, target_levels)
        
        if not highest_education:
            return []
        
        return highest_education['keywords_found']

# Initialize enhanced matcher
education_matcher = EnhancedEducationMatcher()

# Legacy functions for backward compatibility
SKILL_PATTERN = re.compile(r"\b([A-Za-z][A-Za-z+#\.\-]+)\b")
YEARS_PATTERN = re.compile(r"(\d+)\s*(?:\+?\s*)?(?:years|yrs|year)\b", re.IGNORECASE)

def score_skills_and_experience(text: str, required_skills: List[str], min_years: int) -> float:
    text_lower = text.lower()
    score = 0.0
    for skill in required_skills:
        if skill.lower() in text_lower:
            score += 1.0
    years = 0
    for m in YEARS_PATTERN.finditer(text_lower):
        try:
            years = max(years, int(m.group(1)))
        except ValueError:
            continue
    if years >= min_years:
        score += 0.5
    return score

def score_education(text: str, levels: List[str]) -> float:
    """Enhanced education scoring using the new matcher"""
    highest_education = education_matcher.get_highest_education(text, levels)
    
    if not highest_education:
        return 0.0
    
    # Return confidence as score
    return highest_education['confidence']

def keyword_filter_education(text: str, levels: List[str]) -> bool:
    """Enhanced education filtering using the new matcher"""
    return education_matcher.strict_education_filter(text, levels)

def find_education_keywords(text: str, levels: List[str]) -> List[str]:
    """Enhanced education keyword finding using the new matcher"""
    return education_matcher.get_education_keywords_found(text, levels)

# Resume mapping helpers
def _strip_cleaned_suffix(name: str) -> str:
    base = os.path.splitext(name)[0]
    base = re.sub(r"(?i)_avesta_cleaned$", "_Avesta", base)
    base = re.sub(r"(?i)_cleaned$", "", base)
    return base

def find_original_resume(cleaned_id: str) -> str | None:
    if not os.path.isdir(ORIGINAL_RESUMES_FOLDER):
        return None
    preferred_bases = []
    preferred_bases.append(_strip_cleaned_suffix(cleaned_id))
    preferred_bases.append(re.sub(r"(?i)_avesta_cleaned$", "", os.path.splitext(cleaned_id)[0]))
    preferred_bases.append(os.path.splitext(cleaned_id)[0])

    originals = [f for f in os.listdir(ORIGINAL_RESUMES_FOLDER) if os.path.isfile(os.path.join(ORIGINAL_RESUMES_FOLDER, f))]
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

def display_name_from_id(file_id: str) -> str:
    stem = os.path.splitext(file_id)[0]
    parts = stem.split("_")
    return parts[0].strip() if parts else stem.strip()

# Initialize index at startup
index_if_needed()

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/api/search/jd")
def api_search_jd():
    jd = request.form.get("jd", "").strip()
    if not jd:
        return jsonify({"results": []})
    results = search_profiles(jd, top_k=5, include_notes=False)
    payload = []
    for rid, doc, dist, meta in results:
        preview = " ".join(doc.split()[:50]) + "..."
        original = find_original_resume(rid)
        payload.append({
            "id": rid,
            "name": display_name_from_id(rid),
            "similarity": round(1 - float(dist), 4),
            "preview": preview,
            "type": (meta.get("type") if isinstance(meta, dict) else None),
            "resume": original,
        })
    return jsonify({"results": payload})

@app.post("/api/search/skills")
def api_search_skills():
    skills_input = request.form.get("skills", "").strip()
    years_input = request.form.get("years", "0").strip()
    try:
        min_years = int(re.findall(r"\d+", years_input)[0]) if years_input else 0
    except Exception:
        min_years = 0
    skills = [s.strip() for s in skills_input.split(",") if s.strip()]

    semantic_query = ", ".join(skills) + (f", {min_years} years" if min_years else "")
    candidates = search_profiles(semantic_query, top_k=10, include_notes=False)
    rescored = []
    for rid, doc, dist, meta in candidates:
        skill_score = score_skills_and_experience(doc, skills, min_years)
        combined = (1 - dist) + 0.3 * skill_score
        rescored.append((combined, rid, doc, dist, meta))
    rescored.sort(reverse=True)

    payload = []
    for combined, rid, doc, dist, meta in rescored[:5]:
        preview = " ".join(doc.split()[:50]) + "..."
        original = find_original_resume(rid)
        payload.append({
            "id": rid,
            "name": display_name_from_id(rid),
            "score": round(float(combined), 4),
            "similarity": round(1 - float(dist), 4),
            "preview": preview,
            "type": (meta.get("type") if isinstance(meta, dict) else None),
            "resume": original,
        })
    return jsonify({"results": payload})

@app.post("/api/search/education")
def api_search_education():
    edu_input = request.form.get("levels", "").strip()
    levels = [e.strip() for e in edu_input.split(",") if e.strip()]
    semantic_query = "candidates with " + ", ".join(levels)
    candidates = search_profiles(semantic_query, top_k=30, include_notes=False)
    
    # Use enhanced education filtering
    keyword_filtered = []
    for rid, doc, dist, meta in candidates:
        if keyword_filter_education(doc, levels):
            keyword_filtered.append((rid, doc, dist, meta))
    
    if keyword_filtered:
        rescored = []
        for rid, doc, dist, meta in keyword_filtered:
            edu_score = score_education(doc, levels)
            combined = (1 - dist) + 0.4 * edu_score
            rescored.append((combined, rid, doc, dist, meta))
        rescored.sort(reverse=True)
        search_type = f"Enhanced Keyword Match ({len(keyword_filtered)} found)"
    else:
        # Fallback to semantic search with scoring
        rescored = []
        for rid, doc, dist, meta in candidates:
            edu_score = score_education(doc, levels)
            combined = (1 - dist) + 0.4 * edu_score
            rescored.append((combined, rid, doc, dist, meta))
        rescored.sort(reverse=True)
        search_type = "Enhanced Semantic Search (No exact keyword matches)"

    payload = []
    for combined, rid, doc, dist, meta in rescored[:5]:
        preview = " ".join(doc.split()[:50]) + "..."
        original = find_original_resume(rid)
        
        # Find education keywords for highlighting
        found_keywords = find_education_keywords(doc, levels)
        education_highlight = ", ".join(found_keywords) if found_keywords else "No specific education keywords found"
        
        payload.append({
            "id": rid,
            "name": display_name_from_id(rid),
            "score": round(float(combined), 4),
            "similarity": round(1 - float(dist), 4),
            "preview": preview,
            "type": (meta.get("type") if isinstance(meta, dict) else None),
            "resume": original,
            "search_type": search_type,
            "education_keywords": education_highlight,
            "found_keywords": found_keywords
        })
    return jsonify({"results": payload, "search_type": search_type})

@app.post("/api/search/general")
def api_search_general():
    q = request.form.get("q", "").strip()
    include_notes = request.form.get("include_notes", "n").lower() == "y"
    results = search_profiles(q, top_k=5, include_notes=include_notes)
    payload = []
    for rid, doc, dist, meta in results:
        preview = " ".join(doc.split()[:50]) + "..."
        original = find_original_resume(rid)
        payload.append({
            "id": rid,
            "name": display_name_from_id(rid),
            "similarity": round(1 - float(dist), 4),
            "preview": preview,
            "type": (meta.get("type") if isinstance(meta, dict) else None),
            "resume": original,
        })
    return jsonify({"results": payload})

@app.get("/resume/<path:filename>")
def serve_resume(filename: str):
    safe_path = os.path.join(ORIGINAL_RESUMES_FOLDER, filename)
    if os.path.isfile(safe_path):
        return send_from_directory(ORIGINAL_RESUMES_FOLDER, os.path.basename(safe_path), as_attachment=False)
    return ("File not found", 404)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

