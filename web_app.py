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


# --- Resume mapping helpers (map cleaned text IDs to original files in resumes/) ---
def _strip_cleaned_suffix(name: str) -> str:
    base = os.path.splitext(name)[0]
    # Common patterns observed: _Avesta_cleaned, _AVesta_cleaned, etc.
    base = re.sub(r"(?i)_avesta_cleaned$", "_Avesta", base)
    base = re.sub(r"(?i)_cleaned$", "", base)
    return base


def find_original_resume(cleaned_id: str) -> str | None:
    if not os.path.isdir(ORIGINAL_RESUMES_FOLDER):
        return None
    preferred_bases = []
    preferred_bases.append(_strip_cleaned_suffix(cleaned_id))
    # Also consider removing trailing markers entirely
    preferred_bases.append(re.sub(r"(?i)_avesta_cleaned$", "", os.path.splitext(cleaned_id)[0]))
    preferred_bases.append(os.path.splitext(cleaned_id)[0])

    originals = [f for f in os.listdir(ORIGINAL_RESUMES_FOLDER) if os.path.isfile(os.path.join(ORIGINAL_RESUMES_FOLDER, f))]
    originals_lower = [f.lower() for f in originals]

    # Exact basename + extension tries
    for base in preferred_bases:
        for ext in (".pdf", ".docx"):
            candidate = base + ext
            if candidate in originals or candidate.lower() in originals_lower:
                # Return the exact cased original filename
                if candidate in originals:
                    return candidate
                return originals[originals_lower.index(candidate.lower())]

    # Fuzzy startswith match on stem
    for base in preferred_bases:
        base_lower = base.lower()
        for orig, orig_l in zip(originals, originals_lower):
            stem = os.path.splitext(orig_l)[0]
            if stem.startswith(base_lower) and (orig_l.endswith('.pdf') or orig_l.endswith('.docx')):
                return orig
    return None


def display_name_from_id(file_id: str) -> str:
    # Example: "Mohammed Idris_Data Engineer_ZGN_Avesta_cleaned.txt" -> "Mohammed Idris"
    stem = os.path.splitext(file_id)[0]
    parts = stem.split("_")
    return parts[0].strip() if parts else stem.strip()

# Initialize index at startup (Flask 3 has no before_first_request)
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
    candidates = search_profiles(semantic_query, top_k=10, include_notes=False)
    rescored = []
    for rid, doc, dist, meta in candidates:
        edu_score = score_education(doc, levels)
        combined = (1 - dist) + 0.4 * edu_score
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
    # Only serve files that physically exist inside the resumes/ folder
    safe_path = os.path.join(ORIGINAL_RESUMES_FOLDER, filename)
    if os.path.isfile(safe_path):
        return send_from_directory(ORIGINAL_RESUMES_FOLDER, os.path.basename(safe_path), as_attachment=False)
    return ("File not found", 404)


if __name__ == "__main__":
    # For local usage
    app.run(host="0.0.0.0", port=5000, debug=True)


