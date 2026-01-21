#!/usr/bin/env python3
"""
Fixed Education Matcher - Addresses the issues found in the diagnostic
"""

import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class EducationMatch:
    level: str
    confidence: float
    context: str
    keywords_found: List[str]

class FixedEducationMatcher:
    """
    Improved education matcher that addresses the issues found:
    1. Prevents multiple conflicting education levels
    2. Uses context-aware matching
    3. Handles edge cases like "B.T ech" (with space)
    4. Prioritizes highest education level
    """
    
    def __init__(self):
        # More precise patterns with better word boundaries
        self.education_patterns = {
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
        
        # Education hierarchy (higher number = higher education)
        self.education_hierarchy = {
            'bachelors': 1,
            'masters': 2, 
            'phd': 3
        }
    
    def extract_education_section(self, text: str) -> str:
        """Extract education section with better context detection"""
        lines = text.split('\n')
        education_lines = []
        in_education = False
        education_keywords = ['education', 'qualification', 'degree', 'academic', 'university', 'college', 'institute', 'school']
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check if we're entering education section
            if any(keyword in line_lower for keyword in education_keywords):
                in_education = True
                education_lines.append(line)
                continue
            
            # If we're in education section, collect lines
            if in_education:
                # Stop if we hit another major section (but be more specific)
                if any(section in line_lower for section in ['experience', 'work history', 'professional experience', 'skills', 'projects', 'certification', 'achievements']):
                    break
                education_lines.append(line)
        
        return '\n'.join(education_lines)
    
    def find_education_matches(self, text: str, target_levels: List[str] = None) -> List[EducationMatch]:
        """Find education matches with context awareness"""
        text_lower = text.lower()
        education_section = self.extract_education_section(text)
        education_section_lower = education_section.lower()
        
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
                # Calculate confidence based on context
                confidence = self.calculate_confidence(keywords_found, education_section_lower, level)
                
                matches.append(EducationMatch(
                    level=level,
                    confidence=confidence,
                    context=education_section,
                    keywords_found=keywords_found
                ))
        
        return matches
    
    def calculate_confidence(self, keywords_found: List[str], education_section: str, level: str) -> float:
        """Calculate confidence score for education match"""
        base_confidence = 0.5
        
        # Higher confidence if found in education section
        if any(keyword in education_section for keyword in keywords_found):
            base_confidence += 0.3
        
        # Higher confidence for more specific keywords
        specific_keywords = ['phd', 'doctorate', 'masters', 'mba', 'btech', 'bachelor']
        if any(keyword in keywords_found for keyword in specific_keywords):
            base_confidence += 0.2
        
        # Penalize if found in non-education context
        if 'experience' in education_section or 'work' in education_section:
            base_confidence -= 0.1
        
        return min(1.0, max(0.0, base_confidence))
    
    def get_highest_education(self, text: str, target_levels: List[str] = None) -> EducationMatch:
        """Get the highest education level found, resolving conflicts"""
        matches = self.find_education_matches(text, target_levels)
        
        if not matches:
            return None
        
        # If multiple levels found, prioritize the highest
        if len(matches) > 1:
            # Sort by education hierarchy (PhD > Masters > Bachelors)
            matches.sort(key=lambda x: self.education_hierarchy.get(x.level, 0), reverse=True)
            
            # Return the highest level with good confidence
            for match in matches:
                if match.confidence > 0.6:
                    return match
            
            # If no high confidence match, return the highest level
            return matches[0]
        
        return matches[0]
    
    def strict_education_filter(self, text: str, target_levels: List[str]) -> bool:
        """Strict filtering that only returns True for exact matches"""
        highest_education = self.get_highest_education(text, target_levels)
        
        if not highest_education:
            return False
        
        # Only return True if the highest education matches one of the target levels
        return highest_education.level in [level.lower() for level in target_levels]
    
    def get_education_keywords_found(self, text: str, target_levels: List[str]) -> List[str]:
        """Get the specific education keywords found for highlighting"""
        highest_education = self.get_highest_education(text, target_levels)
        
        if not highest_education:
            return []
        
        return highest_education.keywords_found

def test_fixed_matcher():
    """Test the fixed education matcher"""
    print("🧪 TESTING FIXED EDUCATION MATCHER")
    print("=" * 50)
    
    matcher = FixedEducationMatcher()
    
    # Test cases from the diagnostic
    test_cases = [
        {
            'name': 'VAIBHAV SAWHNEY',
            'text': '2015 B.T ech. ECE from ITER, NAME O NAME with 7.21 CGPA 2011 12thf rom NAME School',
            'target_levels': ['phd'],
            'expected': False
        },
        {
            'name': 'Jorawar Singh', 
            'text': 'Mtech In Artificial Intelligence Data Science Engineering JULY 2024 present P UNJABI UNIVERSITY Patiala,Punjab,india Btech In Computer Science Engineering 2015 2019',
            'target_levels': ['masters'],
            'expected': True
        },
        {
            'name': 'Deepika Chavan',
            'text': 'Masters in Computer Science from University of Texas, B.Sc in Mathematics from State University',
            'target_levels': ['masters'],
            'expected': True
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📄 Testing: {test_case['name']}")
        print(f"Text: {test_case['text'][:100]}...")
        print(f"Target levels: {test_case['target_levels']}")
        
        # Test strict filtering
        result = matcher.strict_education_filter(test_case['text'], test_case['target_levels'])
        print(f"Strict filter result: {result}")
        
        # Test highest education detection
        highest = matcher.get_highest_education(test_case['text'], test_case['target_levels'])
        if highest:
            print(f"Highest education: {highest.level} (confidence: {highest.confidence:.2f})")
            print(f"Keywords found: {highest.keywords_found}")
        else:
            print("No education level detected")
        
        # Test keyword highlighting
        keywords = matcher.get_education_keywords_found(test_case['text'], test_case['target_levels'])
        print(f"Keywords for highlighting: {keywords}")

if __name__ == "__main__":
    test_fixed_matcher()

