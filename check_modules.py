#!/usr/bin/env python3
"""Check all required modules for platform_app.py"""

required_modules = {
    'flask': 'Flask',
    'chromadb': 'chromadb',
    'sentence_transformers': 'SentenceTransformer',
    'PyPDF2': 'PdfReader',
    'docx': 'Document',
}

print("Checking required modules...\n")
missing = []
installed = []

for module, attr in required_modules.items():
    try:
        mod = __import__(module, fromlist=[attr])
        getattr(mod, attr)
        installed.append(module)
        print(f"[OK] {module:25}")
    except ImportError as e:
        missing.append(module)
        print(f"[MISSING] {module:25}")
    except AttributeError as e:
        missing.append(module)
        print(f"[MISSING ATTR] {module:25} - {attr}")
    except Exception as e:
        missing.append(module)
        print(f"[ERROR] {module:25} - {type(e).__name__}")

print("\n" + "="*50)
if missing:
    print("\nMISSING MODULES - Install with:")
    print(f"\npip install {' '.join(missing)}")
    
    # Provide specific package names
    package_map = {
        'docx': 'python-docx',
        'sentence_transformers': 'sentence-transformers',
    }
    
    packages_to_install = [package_map.get(m, m) for m in missing]
    print(f"\nOr specifically:")
    print(f"pip install {' '.join(packages_to_install)}")
else:
    print("\n✓ ALL MODULES INSTALLED - Ready to run!")
    print("\nRun: python platform_app.py")
