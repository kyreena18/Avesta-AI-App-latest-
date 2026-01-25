# Dependency Compatibility Fix

## The Problem

Your environment has conflicting dependencies:
- `sentence-transformers` 2.2.2 requires `huggingface_hub < 0.20.0`
- `transformers` 4.55.4 requires `huggingface_hub >= 0.34.0`

This affects both your existing `web_app.py` and the new `platform_app.py`.

## Solution: Use Compatible Versions

The best approach is to install compatible versions that work together. Here are the options:

### Option 1: Downgrade transformers (Recommended)

```powershell
pip install "transformers<4.35.0" "huggingface_hub<0.20.0"
```

This should make everything compatible with sentence-transformers 2.2.2.

### Option 2: Upgrade sentence-transformers (if compatible)

```powershell
pip install --upgrade sentence-transformers
pip install "huggingface_hub>=0.34.0"
```

### Option 3: Use a Virtual Environment (Best Practice)

Create a clean environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Quick Test

After fixing dependencies, test with:

```powershell
python -c "from sentence_transformers import SentenceTransformer; print('OK')"
```

If that works, then:

```powershell
python platform_app.py
```

## Note

This is an environment/dependency issue, not a code issue. The platform code uses the same libraries as your existing Avesta app, so once dependencies are fixed, both should work.
