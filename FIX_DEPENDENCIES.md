# Fix Dependency Compatibility Issue

## Problem

You're encountering an import error:
```
ImportError: cannot import name 'cached_download' from 'huggingface_hub'
```

This happens because `sentence-transformers` 3.0.1 is incompatible with newer versions of `huggingface_hub`.

## Solutions

### Option 1: Downgrade huggingface_hub (Recommended)

```powershell
pip install "huggingface_hub<0.20.0"
```

Then try running again:
```powershell
python platform_app.py
```

### Option 2: Upgrade sentence-transformers

```powershell
pip install --upgrade sentence-transformers
```

### Option 3: Use specific compatible versions

```powershell
pip install sentence-transformers==2.2.2 huggingface_hub==0.16.4
```

## Check Your Existing Setup

If your existing `web_app.py` works, check what versions it uses:
```powershell
python web_app.py
```

If it works, those are the correct versions for your environment. The platform uses the same dependencies, so it should work with the same versions.

## Note

This is a dependency/environment issue, not a code issue. The platform code is correct and uses the same libraries as your existing Avesta app.
