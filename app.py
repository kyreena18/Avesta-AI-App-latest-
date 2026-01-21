import os
import re
from typing import List, Tuple, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer

# ✅ Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLEANED_FOLDER = os.path.join(BASE_DIR, "cleaned_resumes")
INTERVIEW_FOLDER = os.path.join(BASE_DIR, "interview_notes")  # optional folder
CHROMA_PATH = os.path.join(BASE_DIR, "resume_db")

# ✅ Initialize local embedding model (no API keys needed)
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# ✅ Initialize ChromaDB (persistent)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection("resumes")

print("✅ Local embeddings and ChromaDB initialized successfully!")


# ✅ Helper to embed text
def embed_text(text: str) -> List[float]:
    return model.encode([text], normalize_embeddings=True)[0].tolist()


# ✅ Step 1: Load resumes (and interview notes if present)
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


# ✅ Step 2: Index if not already present
def index_if_needed():
    existing = collection.get()
    if len(existing.get("ids", [])) == 0:
        print("⚙️ Indexing resumes...")
        docs, ids, metadatas = load_documents()
        for i, doc in enumerate(docs):
            emb = embed_text(doc)
            collection.add(
                documents=[doc], embeddings=[emb], ids=[ids[i]], metadatas=[metadatas[i]]
            )
        print("✅ All resumes indexed!")
    else:
        print("✅ Index already exists.")


# ✅ Step 3: Search function
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


# ✅ Utility scorers for specialized queries
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


# ✅ Step 4: Interactive Interface
def main():
    print("\n🚀 AVESTA AI RESUME SEARCH SYSTEM")
    print("---------------------------------")
    index_if_needed()

    menu = (
        "\nChoose an option:\n"
        "1) Paste a Job Description to get ranked profiles\n"
        "2) Find profiles by skills and minimum experience (e.g., Python, AWS; 3 years)\n"
        "3) Find profiles by education level (e.g., Masters, PhD)\n"
        "4) General question (optionally include interviewer notes)\n"
        "Type 'exit' to quit.\n> "
    )

    while True:
        choice = input(menu).strip()
        if choice.lower() == "exit":
            break

        if choice == "1":
            print("\nPaste JD (finish with a blank line):")
            lines = []
            while True:
                try:
                    line = input()
                except EOFError:
                    break
                if line.strip() == "":
                    break
                lines.append(line)
            jd = "\n".join(lines).strip()
            if not jd:
                continue
            results = search_profiles(jd, top_k=5, include_notes=False)
            print("\n🔍 Top Matching Profiles for JD:\n")
            for i, (rid, doc, dist, meta) in enumerate(results, 1):
                print(f"{i}. {rid} — similarity: {1 - dist:.2f}")
                preview = " ".join(doc.split()[:50]) + "..."
                print(f"   → {preview}\n")

        elif choice == "2":
            skills_input = input("Enter comma-separated skills (e.g., Python, AWS, NLP):\n> ").strip()
            years_input = input("Minimum total years of experience (number):\n> ").strip()
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
            print("\n🔍 Top Profiles by Skills + Experience:\n")
            for i, (combined, rid, doc, dist, meta) in enumerate(rescored[:5], 1):
                print(f"{i}. {rid} — score: {combined:.2f} (similarity {1 - dist:.2f})")
                preview = " ".join(doc.split()[:50]) + "..."
                print(f"   → {preview}\n")

        elif choice == "3":
            edu_input = input("Desired education levels (comma-separated: Bachelors, Masters, PhD):\n> ").strip()
            levels = [e.strip() for e in edu_input.split(",") if e.strip()]
            semantic_query = "candidates with " + ", ".join(levels)
            candidates = search_profiles(semantic_query, top_k=10, include_notes=False)
            rescored = []
            for rid, doc, dist, meta in candidates:
                edu_score = score_education(doc, levels)
                combined = (1 - dist) + 0.4 * edu_score
                rescored.append((combined, rid, doc, dist, meta))
            rescored.sort(reverse=True)
            print("\n🎓 Top Profiles by Education:\n")
            for i, (combined, rid, doc, dist, meta) in enumerate(rescored[:5], 1):
                print(f"{i}. {rid} — score: {combined:.2f} (similarity {1 - dist:.2f})")
                preview = " ".join(doc.split()[:50]) + "..."
                print(f"   → {preview}\n")

        elif choice == "4":
            q = input("Enter your question:\n> ").strip()
            inc = input("Include interviewer notes? (y/n):\n> ").strip().lower()
            include_notes = inc == "y"
            results = search_profiles(q, top_k=5, include_notes=include_notes)
            print("\n🔍 Top Answers:\n")
            for i, (rid, doc, dist, meta) in enumerate(results, 1):
                tag = meta.get("type", "?") if isinstance(meta, dict) else "?"
                print(f"{i}. {rid} [{tag}] — similarity: {1 - dist:.2f}")
                preview = " ".join(doc.split()[:50]) + "..."
                print(f"   → {preview}\n")

        else:
            print("Please choose 1, 2, 3, 4 or 'exit'.")


if __name__ == "__main__":
    main()
