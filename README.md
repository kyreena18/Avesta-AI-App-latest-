# Avesta AI Resume Search – Simple Guide

Welcome! This is a very simple, beginner‑friendly guide for using the Avesta AI Resume Search web application.

## What you need

- A Windows computer with internet
- Python 3.10 or newer

## Step 1 – Open the folder

1. Find the folder named `Avesta AI App` on your Desktop.
2. Click inside the folder so you can see files like `app.py`, `web_app.py`, `requirements.txt`.

## Step 2 – Install the app (first time only)

1. In the folder, click the address bar (where it shows the folder path), type `powershell` and press Enter.
2. A blue window opens (PowerShell).
3. Copy and paste this command, then press Enter:

```
python -m venv .venv ; .\.venv\Scripts\Activate.ps1 ; python -m pip install --upgrade pip ; pip install -r requirements.txt
```

Wait until it finishes. This installs everything the app needs.

## Step 3 – Start the web application

1. In the same blue window, start the web app:

```
python web_app.py
```

2. Wait until you see a line that says something like: `Running on http://127.0.0.1:5000`.
3. Open your browser (Chrome/Edge) and go to `http://127.0.0.1:5000`.

You will see the Avesta AI Resume Search page.

### How to use the web application

The web page has 4 search options:

1) **Job Description** → Paste a job description, click Search. You will see top matching candidates. Click "Open resume" to view the original PDF/DOCX.

2) **Skills + Minimum Experience** → Type skills like `Python, AWS` and a number of years, then Search.

3) **Education Level** → Type levels like `Masters, PhD`, then Search.

4) **General Question** → Type any question. Tick "Include interview notes" if you want notes included.

**Tip:** The first time you search, the app may take a moment to "prepare" (it builds an index). Next time is faster.

## Where to put resumes

- Original resumes (PDF/DOCX) go in the `resumes` folder.
- Cleaned text versions go in the `cleaned_resumes` folder. These are used for searching.
- Optional: interviewer notes (plain text) go in the `interview_notes` folder.

When you click “Open resume”, the app tries to open the matching original file in the `resumes` folder.

## Troubleshooting

- If you see an error about Python not found, install Python from the Microsoft Store or from `https://python.org`.
- If the web page won’t open, make sure `python web_app.py` is still running. Don’t close the blue window.
- If searches show “No results”, check that you have files inside `cleaned_resumes`.
- If “Open resume” says “File not found”, make sure the original PDF/DOCX is inside the `resumes` folder.

## Stopping the app

- Click inside the blue window and press `Ctrl + C` to stop.

That’s it! You’re ready to use Avesta AI.



