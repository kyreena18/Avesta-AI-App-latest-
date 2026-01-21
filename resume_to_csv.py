import os
import re
import pandas as pd
import pdfplumber
import docx
import spacy

nlp = spacy.load("en_core_web_sm")

RESUME_DIR = "C:/Users/Kyreena/OneDrive/Desktop/Resume Finder AI App/Avesta AI App/resumes"

def extract_text(file_path):
    text = ""
    if file_path.endswith(".pdf"):
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text.strip()

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else ""

def extract_phone(text):
    match = re.search(r'(\+?\d[\d\s\-]{8,}\d)', text)
    return match.group(0) if match else ""

def extract_name(text):
    doc = nlp(text[:300])
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return ""

def extract_section(text, keywords):
    lines = text.splitlines()
    section = []
    capture = False
    for line in lines:
        if any(k.lower() in line.lower() for k in keywords):
            capture = True
            continue
        if capture and line.strip() == "":
            break
        if capture:
            section.append(line.strip())
    return " ".join(section)

data = []

for file in os.listdir(RESUME_DIR):
    if file.endswith((".pdf", ".docx")):
        path = os.path.join(RESUME_DIR, file)
        text = extract_text(path)

        row = {
            "Name": extract_name(text),
            "Email": extract_email(text),
            "Phone": extract_phone(text),
            "Skills": extract_section(text, ["skills"]),
            "Education": extract_section(text, ["education"]),
            "Experience": extract_section(text, ["experience", "employment"]),
            "Projects": extract_section(text, ["projects"]),
            "Resume_Text": text[:1000]
        }
        data.append(row)

df = pd.DataFrame(data)
df.to_csv("resumes.csv", index=False)

print("✅ CSV file created: resumes.csv")
