import os
import pickle
from docx import Document
import PyPDF2

# Folder containing resumes
folder = "resumes"

texts = {}

for filename in os.listdir(folder):
    path = os.path.join(folder, filename)

    if filename.endswith(".pdf"):
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif filename.endswith(".docx"):
        doc = Document(path)
        text = " ".join([para.text for para in doc.paragraphs])
    else:
        continue

    texts[filename] = text

# Save extracted text
with open("resumes_texts.pkl", "wb") as f:
    pickle.dump(texts, f)

print("✅ Saved resumes_texts.pkl with extracted text!")
