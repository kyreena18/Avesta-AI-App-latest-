#!/usr/bin/env python3
"""
Diagnostic script to identify education matching issues in the resume search system.
This script will analyze the cleaned resumes and identify why incorrect education matches occur.
"""

import os
import re
from typing import List, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer

# Initialize components
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLEANED_FOLDER = os.path.join(BASE_DIR, "cleaned_resumes")
CHROMA_PATH = os.path.join(BASE_DIR, "resume_db")

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection("resumes")

def analyze_education_patterns():
    """Analyze education patterns in all cleaned resumes"""
    print("🔍 ANALYZING EDUCATION PATTERNS IN CLEANED RESUMES")
    print("=" * 60)
    
    # Enhanced education patterns with better regex
    education_patterns = {
        'phd': [
            r'\b(?:ph\.?d\.?|doctor of philosophy|doctorate|doctoral|d\.phil|dphil)\b',
            r'\b(?:phd|ph\.d|ph\.d\.|doctor of philosophy|doctorate|doctoral|d\.phil|dphil)\b'
        ],
        'masters': [
            r'\b(?:m\.?s\.?|m\.?tech|mtech|m\.?sc|msc|master of|mba|m\.?e\.?|me|mca|m\.?com|mcom|m\.?a\.?|ma|master\'s|master degree)\b',
            r'\b(?:m\.s\.|ms|m\.tech|mtech|m\.sc|msc|master of|mba|m\.e\.|me|mca|m\.com|mcom|m\.a\.|ma|master\'s|master degree)\b'
        ],
        'bachelors': [
            r'\b(?:b\.?e\.?|btech|b\.?tech|b\.?sc|bsc|bca|b\.?eng|bachelor of|bachelor\'s|b\.?com|bcom|b\.?a\.?|ba|bachelor degree|bachelor of technology|bachelor of engineering)\b',
            r'\b(?:b\.e\.|btech|b\.tech|b\.sc|bsc|bca|b\.eng|bachelor of|bachelor\'s|b\.com|bcom|b\.a\.|ba|bachelor degree|bachelor of technology|bachelor of engineering)\b'
        ]
    }
    
    # Get all documents from ChromaDB
    all_docs = collection.get()
    doc_ids = all_docs.get('ids', [])
    documents = all_docs.get('documents', [])
    
    print(f"📊 Found {len(documents)} indexed documents")
    print()
    
    # Analyze each document
    results = []
    for i, (doc_id, document) in enumerate(zip(doc_ids, documents)):
        print(f"📄 Analyzing: {doc_id}")
        
        doc_analysis = {
            'id': doc_id,
            'education_found': [],
            'education_details': [],
            'raw_education_section': '',
            'issues': []
        }
        
        # Look for education section
        education_section = extract_education_section(document)
        doc_analysis['raw_education_section'] = education_section
        
        # Check each education level
        for level, patterns in education_patterns.items():
            found_keywords = []
            for pattern in patterns:
                matches = re.findall(pattern, document, re.IGNORECASE)
                if matches:
                    found_keywords.extend(matches)
                    doc_analysis['education_found'].append(level)
                    doc_analysis['education_details'].append({
                        'level': level,
                        'keywords': matches,
                        'pattern': pattern
                    })
        
        # Check for common issues
        if 'btech' in document.lower() and 'phd' in doc_analysis['education_found']:
            doc_analysis['issues'].append("B.Tech mentioned but PhD detected")
        
        if 'bsc' in document.lower() and 'masters' in doc_analysis['education_found']:
            doc_analysis['issues'].append("B.Sc mentioned but Masters detected")
            
        # Check for multiple conflicting degrees
        if len(set(doc_analysis['education_found'])) > 1:
            doc_analysis['issues'].append(f"Multiple education levels detected: {doc_analysis['education_found']}")
        
        results.append(doc_analysis)
        
        # Print analysis for this document
        print(f"   Education found: {doc_analysis['education_found']}")
        if doc_analysis['issues']:
            print(f"   ⚠️  Issues: {doc_analysis['issues']}")
        print(f"   Education section: {education_section[:100]}...")
        print()
    
    return results

def extract_education_section(document: str) -> str:
    """Extract education section from document"""
    # Look for education-related keywords
    education_keywords = ['education', 'qualification', 'degree', 'academic', 'university', 'college', 'institute']
    
    lines = document.split('\n')
    education_lines = []
    in_education_section = False
    
    for line in lines:
        line_lower = line.lower()
        
        # Check if we're entering education section
        if any(keyword in line_lower for keyword in education_keywords):
            in_education_section = True
            education_lines.append(line)
            continue
        
        # If we're in education section, collect lines
        if in_education_section:
            # Stop if we hit another major section
            if any(section in line_lower for section in ['experience', 'work', 'skills', 'projects', 'certification']):
                break
            education_lines.append(line)
    
    return '\n'.join(education_lines)

def test_education_search():
    """Test the current education search functionality"""
    print("\n🧪 TESTING EDUCATION SEARCH FUNCTIONALITY")
    print("=" * 50)
    
    # Test queries
    test_cases = [
        {'query': 'PhD', 'expected_levels': ['phd']},
        {'query': 'Masters', 'expected_levels': ['masters']},
        {'query': 'Bachelors', 'expected_levels': ['bachelors']},
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['query']}")
        
        # Get semantic results
        query_embedding = model.encode([test_case['query']], normalize_embeddings=True)[0].tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            where={"type": "resume"}
        )
        
        print(f"   Semantic results: {len(results['ids'][0])} found")
        
        # Test keyword filtering
        keyword_matches = []
        for i, (doc_id, document) in enumerate(zip(results['ids'][0], results['documents'][0])):
            if keyword_filter_education(document, test_case['expected_levels']):
                keyword_matches.append((doc_id, document))
        
        print(f"   Keyword matches: {len(keyword_matches)} found")
        
        for doc_id, doc in keyword_matches:
            found_keywords = find_education_keywords(doc, test_case['expected_levels'])
            print(f"     - {doc_id}: {found_keywords}")

def keyword_filter_education(text: str, levels: List[str]) -> bool:
    """Current keyword filtering function from web_app.py"""
    text_lower = text.lower()
    keywords = {
        "phd": ["phd", "doctor of philosophy", "ph.d", "ph.d.", "doctorate", "doctoral", "d.phil", "dphil"],
        "masters": ["masters", "m.s.", "ms ", "m.tech", "mtech", "m.sc", "msc", "master of", "mba", "m.e.", "me ", "mca", "m.com", "mcom", "m.a.", "ma ", "m.sc.", "msc", "master's", "master degree"],
        "bachelors": ["bachelors", "b.e.", "btech", "b.tech", "b.sc", "bsc", "bca", "b.eng", "bachelor of", "bachelor's", "b.com", "bcom", "b.a.", "ba ", "b.sc.", "bsc", "bachelor degree", "bachelor of technology", "bachelor of engineering"],
    }
    
    for level in levels:
        level_lower = level.lower()
        if level_lower in keywords:
            for kw in keywords[level_lower]:
                if kw in text_lower:
                    return True
    return False

def find_education_keywords(text: str, levels: List[str]) -> List[str]:
    """Current education keyword finding function from web_app.py"""
    text_lower = text.lower()
    found_keywords = []
    keywords = {
        "phd": ["phd", "doctor of philosophy", "ph.d", "ph.d.", "doctorate", "doctoral", "d.phil", "dphil"],
        "masters": ["masters", "m.s.", "ms ", "m.tech", "mtech", "m.sc", "msc", "master of", "mba", "m.e.", "me ", "mca", "m.com", "mcom", "m.a.", "ma ", "m.sc.", "msc", "master's", "master degree"],
        "bachelors": ["bachelors", "b.e.", "btech", "b.tech", "b.sc", "bsc", "bca", "b.eng", "bachelor of", "bachelor's", "b.com", "bcom", "b.a.", "ba ", "b.sc.", "bsc", "bachelor degree", "bachelor of technology", "bachelor of engineering"],
    }
    
    for level in levels:
        level_lower = level.lower()
        if level_lower in keywords:
            for kw in keywords[level_lower]:
                if kw in text_lower:
                    found_keywords.append(kw)
    return found_keywords

def create_improved_education_matcher():
    """Create an improved education matching system"""
    print("\n🔧 CREATING IMPROVED EDUCATION MATCHER")
    print("=" * 50)
    
    class ImprovedEducationMatcher:
        def __init__(self):
            # More precise patterns with word boundaries
            self.patterns = {
                'phd': [
                    r'\b(?:ph\.?d\.?|doctor of philosophy|doctorate|doctoral|d\.phil|dphil)\b',
                    r'\b(?:phd|ph\.d|ph\.d\.|doctor of philosophy|doctorate|doctoral|d\.phil|dphil)\b'
                ],
                'masters': [
                    r'\b(?:m\.?s\.?|m\.?tech|mtech|m\.?sc|msc|master of|mba|m\.?e\.?|me|mca|m\.?com|mcom|m\.?a\.?|ma|master\'s|master degree)\b',
                    r'\b(?:m\.s\.|ms|m\.tech|mtech|m\.sc|msc|master of|mba|m\.e\.|me|mca|m\.com|mcom|m\.a\.|ma|master\'s|master degree)\b'
                ],
                'bachelors': [
                    r'\b(?:b\.?e\.?|btech|b\.?tech|b\.?sc|bsc|bca|b\.?eng|bachelor of|bachelor\'s|b\.?com|bcom|b\.?a\.?|ba|bachelor degree|bachelor of technology|bachelor of engineering)\b',
                    r'\b(?:b\.e\.|btech|b\.tech|b\.sc|bsc|bca|b\.eng|bachelor of|bachelor\'s|b\.com|bcom|b\.a\.|ba|bachelor degree|bachelor of technology|bachelor of engineering)\b'
                ]
            }
        
        def match_education(self, text: str, target_levels: List[str]) -> Dict[str, Any]:
            """Improved education matching with context awareness"""
            text_lower = text.lower()
            results = {
                'matches': [],
                'confidence': 0.0,
                'context': '',
                'issues': []
            }
            
            # Extract education section
            education_section = self.extract_education_context(text)
            results['context'] = education_section
            
            # Check each target level
            for level in target_levels:
                level_lower = level.lower()
                if level_lower in self.patterns:
                    for pattern in self.patterns[level_lower]:
                        matches = re.findall(pattern, text_lower)
                        if matches:
                            results['matches'].append({
                                'level': level,
                                'keywords': matches,
                                'pattern': pattern
                            })
            
            # Calculate confidence based on context
            if results['matches']:
                # Higher confidence if found in education section
                if any(edu_word in education_section.lower() for edu_word in ['education', 'qualification', 'degree']):
                    results['confidence'] = 0.9
                else:
                    results['confidence'] = 0.6
                
                # Check for conflicts
                if len(results['matches']) > 1:
                    results['issues'].append("Multiple education levels detected")
            
            return results
        
        def extract_education_context(self, text: str) -> str:
            """Extract education-related context from text"""
            lines = text.split('\n')
            education_lines = []
            in_education = False
            
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in ['education', 'qualification', 'degree', 'academic']):
                    in_education = True
                    education_lines.append(line)
                elif in_education and any(section in line_lower for section in ['experience', 'work', 'skills']):
                    break
                elif in_education:
                    education_lines.append(line)
            
            return '\n'.join(education_lines)
    
    return ImprovedEducationMatcher()

def main():
    """Main diagnostic function"""
    print("🚀 EDUCATION MATCHING DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Step 1: Analyze current patterns
    results = analyze_education_patterns()
    
    # Step 2: Test current search functionality
    test_education_search()
    
    # Step 3: Create improved matcher
    improved_matcher = create_improved_education_matcher()
    
    # Step 4: Test improved matcher
    print("\n🧪 TESTING IMPROVED MATCHER")
    print("=" * 40)
    
    # Test with sample documents
    sample_docs = [
        ("VAIBHAV SAWHNEY", "2015 B.T ech. ECE from ITER"),
        ("Jorawar Singh", "Mtech In Artificial Intelligence Data Science Engineering JULY 2024 present P UNJABI UNIVERSITY Patiala,Punjab,india Btech In Computer Science Engineering 2015 2019")
    ]
    
    for name, text in sample_docs:
        print(f"\n📄 Testing: {name}")
        print(f"Text: {text}")
        
        # Test with different education levels
        for level in ['phd', 'masters', 'bachelors']:
            result = improved_matcher.match_education(text, [level])
            print(f"   {level.upper()}: {result['matches']} (confidence: {result['confidence']})")
            if result['issues']:
                print(f"   Issues: {result['issues']}")

if __name__ == "__main__":
    main()

