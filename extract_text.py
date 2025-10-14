import os
import PyPDF2
import docx

# Paths
resume_folder = "C:/Users/Kyreena/OneDrive/Desktop/Avesta AI App/resumes"
output_folder = "C:/Users/Kyreena/OneDrive/Desktop/Avesta AI App/processed resumes"

# Make sure output folder exists
os.makedirs(output_folder, exist_ok=True)

resumes_texts = []   # <--- create a list to hold all extracted texts

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_path):
    text = ""
    doc = docx.Document(file_path)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def save_text(file_name, text):
    with open(os.path.join(output_folder, file_name + ".txt"), "w", encoding="utf-8") as f:
        f.write(text)

# Go through resumes folder
for file in os.listdir(resume_folder):
    file_path = os.path.join(resume_folder, file)
    file_name, ext = os.path.splitext(file)

    if ext.lower() == ".pdf":
        text = extract_text_from_pdf(file_path)
        save_text(file_name, text)
        resumes_texts.append(text)   # <--- store in list too

    elif ext.lower() == ".docx":
        text = extract_text_from_docx(file_path)
        save_text(file_name, text)
        resumes_texts.append(text)   # <--- store in list too

    else:
        print(f"Skipping {file}, not a PDF or DOCX.")

# (Optional) print number of resumes processed
print(f"Extracted {len(resumes_texts)} resumes")
