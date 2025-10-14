import os
import re

input_folder = "C:/Users/Kyreena/OneDrive/Desktop/Avesta AI App/processed resumes"
output_folder = "C:/Users/Kyreena/OneDrive/Desktop/Avesta AI App/cleaned_resumes"
os.makedirs(output_folder, exist_ok=True)

def clean_resume(text):
    # Basic cleaning: remove extra spaces, non-alphanumeric chars
    text = re.sub(r'\s+', ' ', text)  # remove extra spaces/newlines
    text = re.sub(r'[^\w\s.,]', '', text)  # keep only words, numbers, punctuation
    return text.strip()

for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as f:
            raw_text = f.read()

        cleaned_text = clean_resume(raw_text)

        # save into cleaned_resumes folder
        with open(os.path.join(output_folder, filename), "w", encoding="utf-8") as f:
            f.write(cleaned_text)

print("✅ All resumes cleaned and saved in 'cleaned_resumes'")
