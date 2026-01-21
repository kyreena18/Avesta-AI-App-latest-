#!/usr/bin/env python3
"""
Quick test of the education matching fixes
"""

import re
from typing import List, Dict, Any

class QuickEducationMatcher:
    def __init__(self):
        self.education_patterns = {
            'phd': [
                r'\b(?:ph\.?d\.?|doctor of philosophy|doctorate|doctoral|d\.phil|dphil)\b'
            ],
            'masters': [
                r'\b(?:m\.?s\.?|m\.?tech|mtech|m\.?sc|msc|master of|mba|m\.?e\.?|me|mca|m\.?com|mcom|m\.?a\.?|ma|master\'s|master degree)\b'
            ],
            'bachelors': [
                r'\b(?:b\.?e\.?|btech|b\.?tech|b\.?sc|bsc|bca|b\.?eng|bachelor of|bachelor\'s|b\.?com|bcom|b\.?a\.?|ba|bachelor degree|bachelor of technology|bachelor of engineering)\b'
            ]
        }
        
        self.education_hierarchy = {
            'bachelors': 1,
            'masters': 2, 
            'phd': 3
        }
    
    def get_highest_education(self, text: str, target_levels: List[str] = None) -> Dict[str, Any]:
        """Get the highest education level found"""
        text_lower = text.lower()
        matches = []
        levels_to_check = target_levels if target_levels else ['phd', 'masters', 'bachelors']
        
        for level in levels_to_check:
            if level not in self.education_patterns:
                continue
                
            keywords_found = []
            for pattern in self.education_patterns[level]:
                pattern_matches = re.findall(pattern, text_lower)
                if pattern_matches:
                    keywords_found.extend(pattern_matches)
            
            if keywords_found:
                matches.append({
                    'level': level,
                    'confidence': 0.8,  # Simplified confidence
                    'keywords_found': keywords_found
                })
        
        if not matches:
            return None
        
        # If multiple levels found, prioritize the highest
        if len(matches) > 1:
            matches.sort(key=lambda x: self.education_hierarchy.get(x['level'], 0), reverse=True)
        
        return matches[0]
    
    def strict_education_filter(self, text: str, target_levels: List[str]) -> bool:
        """Strict filtering that only returns True for exact matches"""
        highest_education = self.get_highest_education(text, target_levels)
        
        if not highest_education:
            return False
        
        return highest_education['level'] in [level.lower() for level in target_levels]

def test_quick_matcher():
    """Test the quick education matcher"""
    print("🧪 TESTING QUICK EDUCATION MATCHER")
    print("=" * 50)
    
    matcher = QuickEducationMatcher()
    
    # Test cases
    test_cases = [
        {
            'name': 'B.Tech only',
            'text': '2015 B.T ech. ECE from ITER',
            'target_levels': ['phd'],
            'expected': False
        },
        {
            'name': 'M.Tech + B.Tech',
            'text': 'Mtech In Artificial Intelligence Data Science Engineering Btech In Computer Science Engineering',
            'target_levels': ['masters'],
            'expected': True
        },
        {
            'name': 'PhD + Masters',
            'text': 'PhD in Computer Science Masters in Mathematics',
            'target_levels': ['phd'],
            'expected': True
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📄 Testing: {test_case['name']}")
        print(f"Text: {test_case['text']}")
        print(f"Target levels: {test_case['target_levels']}")
        
        # Test strict filtering
        result = matcher.strict_education_filter(test_case['text'], test_case['target_levels'])
        print(f"Filter result: {result} (expected: {test_case['expected']})")
        
        # Test highest education
        highest = matcher.get_highest_education(test_case['text'], test_case['target_levels'])
        if highest:
            print(f"Highest education: {highest['level']}")
            print(f"Keywords: {highest['keywords_found']}")
        else:
            print("No education level detected")
        
        print("-" * 30)

if __name__ == "__main__":
    test_quick_matcher()

