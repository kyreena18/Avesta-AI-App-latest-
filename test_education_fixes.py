#!/usr/bin/env python3
"""
Test script to verify the education matching fixes work correctly
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_web_app import education_matcher, keyword_filter_education, find_education_keywords, score_education

def test_education_fixes():
    """Test the fixed education matching with real resume data"""
    print("🧪 TESTING EDUCATION MATCHING FIXES")
    print("=" * 60)
    
    # Test cases based on the issues found
    test_cases = [
        {
            'name': 'VAIBHAV SAWHNEY (B.Tech only)',
            'text': '2015 B.T ech. ECE from ITER, NAME O NAME with 7.21 CGPA 2011 12thf rom NAME School',
            'target_levels': ['phd'],
            'expected_match': False,
            'expected_highest': 'bachelors'
        },
        {
            'name': 'Jorawar Singh (M.Tech + B.Tech)',
            'text': 'Mtech In Artificial Intelligence Data Science Engineering JULY 2024 present P UNJABI UNIVERSITY Patiala,Punjab,india Btech In Computer Science Engineering 2015 2019',
            'target_levels': ['masters'],
            'expected_match': True,
            'expected_highest': 'masters'
        },
        {
            'name': 'Deepika Chavan (Masters + B.Sc)',
            'text': 'Masters in Computer Science from University of Texas, B.Sc in Mathematics from State University',
            'target_levels': ['masters'],
            'expected_match': True,
            'expected_highest': 'masters'
        },
        {
            'name': 'PhD Candidate',
            'text': 'PhD in Computer Science from MIT, Masters in Mathematics from Stanford',
            'target_levels': ['phd'],
            'expected_match': True,
            'expected_highest': 'phd'
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📄 Testing: {test_case['name']}")
        print(f"Text: {test_case['text'][:80]}...")
        print(f"Target levels: {test_case['target_levels']}")
        
        # Test strict filtering
        filter_result = keyword_filter_education(test_case['text'], test_case['target_levels'])
        print(f"✅ Strict filter result: {filter_result} (expected: {test_case['expected_match']})")
        
        # Test highest education detection
        highest = education_matcher.get_highest_education(test_case['text'], test_case['target_levels'])
        if highest:
            print(f"✅ Highest education: {highest['level']} (confidence: {highest['confidence']:.2f})")
            print(f"   Expected highest: {test_case['expected_highest']}")
            print(f"   Keywords found: {highest['keywords_found']}")
        else:
            print("❌ No education level detected")
        
        # Test keyword highlighting
        keywords = find_education_keywords(test_case['text'], test_case['target_levels'])
        print(f"✅ Keywords for highlighting: {keywords}")
        
        # Test scoring
        score = score_education(test_case['text'], test_case['target_levels'])
        print(f"✅ Education score: {score:.2f}")
        
        print("-" * 40)

def test_with_real_resumes():
    """Test with actual cleaned resume files"""
    print("\n📁 TESTING WITH REAL RESUME FILES")
    print("=" * 50)
    
    cleaned_folder = "cleaned_resumes"
    if not os.path.exists(cleaned_folder):
        print(f"❌ Folder {cleaned_folder} not found")
        return
    
    # Test with a few sample files
    sample_files = [
        "VAIBHAV SAWHNEY_Senior Data Scientist – Natural language processing and Computer vision_GHD_Avesta_cleaned.txt",
        "Jorawar Singh_Senior Data Scientist – Natural language processing and Computer vision_GHD_Avesta_cleaned.txt"
    ]
    
    for filename in sample_files:
        filepath = os.path.join(cleaned_folder, filename)
        if not os.path.exists(filepath):
            continue
            
        print(f"\n📄 Testing: {filename}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Test different education level searches
        for target_level in ['phd', 'masters', 'bachelors']:
            print(f"\n   🎯 Searching for: {target_level.upper()}")
            
            # Test filtering
            filter_result = keyword_filter_education(content, [target_level])
            print(f"   Filter result: {filter_result}")
            
            # Test highest education
            highest = education_matcher.get_highest_education(content, [target_level])
            if highest:
                print(f"   Highest education: {highest['level']} (confidence: {highest['confidence']:.2f})")
                print(f"   Keywords: {highest['keywords_found']}")
            else:
                print("   No education level detected")
            
            # Test scoring
            score = score_education(content, [target_level])
            print(f"   Score: {score:.2f}")

def main():
    """Main test function"""
    print("🚀 EDUCATION MATCHING FIXES TEST")
    print("=" * 60)
    
    # Test with synthetic data
    test_education_fixes()
    
    # Test with real resume files
    test_with_real_resumes()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()

