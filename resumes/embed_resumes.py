import os
import pickle
import re
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Path to cleaned resumes
cleaned_folder = "C:/Users/Kyreena/OneDrive/Desktop/Avesta AI App/cleaned_resumes"

# Load cleaned resumes
resumes = []
for file in os.listdir(cleaned_folder):
    if file.endswith(".txt"):
        with open(os.path.join(cleaned_folder, file), "r", encoding="utf-8") as f:
            resumes.append({"filename": file, "text": f.read()})

# Create embeddings for resumes
resume_embeddings = []
for resume in resumes:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=resume["text"]
    )
    embedding = response.data[0].embedding
    resume_embeddings.append({
        "filename": resume["filename"],
        "embedding": embedding,
        "text": resume["text"]
    })

# Save embeddings
with open("resume_embeddings.pkl", "wb") as f:
    pickle.dump(resume_embeddings, f)

print("✅ Resume embeddings created and saved as resume_embeddings.pkl")