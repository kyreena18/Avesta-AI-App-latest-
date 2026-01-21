#!/usr/bin/env python3
"""
Simple diagnostic to identify education matching issues
"""

import os
import re

def analyze_education_issues():
    """Analyze education patterns in cleaned resumes"""
    print("🔍 ANALYZING EDUCATION PATTERNS")
    print("=" * 50)
    
    cleaned_folder = "cleaned_resumes"
    
    # Current education patterns from web_app.py
    keywords = {
        "phd": ["phd", "doctor of philosophy", "ph.d", "ph.d.", "doctorate", "doctoral", "d.phil", "dphil"],
        "masters": ["masters", "m.s.", "ms ", "m.tech", "mtech", "m.sc", "msc", "master of", "mba", "m.e.", "me ", "mca", "m.com", "mcom", "m.a.", "ma ", "m.sc.", "msc", "master's", "master degree"],
        "bachelors": ["bachelors", "b.e.", "btech", "b.tech", "b.sc", "bsc", "bca", "b.eng", "bachelor of", "bachelor's", "b.com", "bcom", "b.a.", "ba ", "b.sc.", "bsc", "bachelor degree", "bachelor of technology", "bachelor of engineering"],
    }
    
    if not os.path.exists(cleaned_folder):
        print(f"❌ Folder {cleaned_folder} not found")
        return
    
    files = [f for f in os.listdir(cleaned_folder) if f.endswith('.txt')]
    print(f"📊 Found {len(files)} cleaned resume files")
    print()
    
    issues_found = []
    
    for filename in files[:5]:  # Analyze first 5 files
        print(f"📄 Analyzing: {filename}")
        
        filepath = os.path.join(cleaned_folder, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for education patterns
        content_lower = content.lower()
        
        found_education = []
        for level, patterns in keywords.items():
            for pattern in patterns:
                if pattern in content_lower:
                    found_education.append(level)
                    print(f"   ✅ Found {level}: '{pattern}'")
        
        # Check for specific issues
        issues = []
        
        # Issue 1: B.Tech mentioned but PhD detected
        if 'btech' in content_lower or 'b.tech' in content_lower:
            if 'phd' in found_education:
                issues.append("B.Tech mentioned but PhD detected")
        
        # Issue 2: B.Sc mentioned but Masters detected  
        if 'bsc' in content_lower or 'b.sc' in content_lower:
            if 'masters' in found_education:
                issues.append("B.Sc mentioned but Masters detected")
        
        # Issue 3: Multiple conflicting degrees
        if len(set(found_education)) > 1:
            issues.append(f"Multiple education levels: {found_education}")
        
        if issues:
            issues_found.extend([(filename, issue) for issue in issues])
            print(f"   ⚠️  Issues: {issues}")
        else:
            print(f"   ✅ No issues found")
        
        print()
    
    # Summary
    print("📋 SUMMARY OF ISSUES FOUND:")
    print("=" * 40)
    if issues_found:
        for filename, issue in issues_found:
            print(f"❌ {filename}: {issue}")
    else:
        print("✅ No issues found in analyzed files")

def test_keyword_matching():
    """Test the current keyword matching logic"""
    print("\n🧪 TESTING KEYWORD MATCHING")
    print("=" * 40)
    
    # Test cases
    test_cases = [
        {
            'text': '2015 B.T ech. ECE from ITER',
            'expected': 'bachelors',
            'description': 'B.Tech degree'
        },
        {
            'text': 'Mtech In Artificial Intelligence Data Science Engineering',
            'expected': 'masters', 
            'description': 'M.Tech degree'
        },
        {
            'text': 'PhD in Computer Science',
            'expected': 'phd',
            'description': 'PhD degree'
        }
    ]
    
    keywords = {
        "phd": ["phd", "doctor of philosophy", "ph.d", "ph.d.", "doctorate", "doctoral", "d.phil", "dphil"],
        "masters": ["masters", "m.s.", "ms ", "m.tech", "mtech", "m.sc", "msc", "master of", "mba", "m.e.", "me ", "mca", "m.com", "mcom", "m.a.", "ma ", "m.sc.", "msc", "master's", "master degree"],
        "bachelors": ["bachelors", "b.e.", "btech", "b.tech", "b.sc", "bsc", "bca", "b.eng", "bachelor of", "bachelor's", "b.com", "bcom", "b.a.", "ba ", "b.sc.", "bsc", "bachelor degree", "bachelor of technology", "bachelor of engineering"],
    }
    
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['description']}")
        print(f"Text: '{test_case['text']}'")
        
        text_lower = test_case['text'].lower()
        found_levels = []
        
        for level, patterns in keywords.items():
            for pattern in patterns:
                if pattern in text_lower:
                    found_levels.append(level)
                    print(f"   ✅ Matched {level}: '{pattern}'")
        
        expected = test_case['expected']
        if expected in found_levels:
            print(f"   ✅ Correctly identified as {expected}")
        else:
            print(f"   ❌ Expected {expected}, found {found_levels}")

if __name__ == "__main__":
    analyze_education_issues()
    test_keyword_matching()

