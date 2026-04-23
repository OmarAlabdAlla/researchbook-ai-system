#!/usr/bin/env python3
"""
Enhanced Name Matching System for ResearchBook
Handles all variations: hyphens, spaces, accents, case, punctuation
"""

import re
import unicodedata
from typing import List, Dict, Any

class EnhancedNameMatcher:
    def __init__(self):
        """Initialize the enhanced name matcher"""
        pass
    
    def normalize_name(self, name: str) -> str:
        """
        Normalize a name for matching by:
        1. Converting to lowercase
        2. Removing accents/diacritics  
        3. Replacing hyphens/punctuation with spaces
        4. Collapsing multiple spaces
        5. Stripping whitespace
        """
        if not name:
            return ""
        
        # Convert to lowercase
        name = name.lower()
        
        # Remove accents and diacritics (José -> jose, Arnäs -> arnas)
        name = unicodedata.normalize('NFD', name)
        name = ''.join(char for char in name if unicodedata.category(char) != 'Mn')
        
        # Replace all punctuation with spaces (hyphens, apostrophes, dots, etc)
        name = re.sub(r'[^\w\s]', ' ', name)
        
        # Collapse multiple spaces and strip
        name = ' '.join(name.split())
        
        return name
    
    def generate_name_variations(self, input_name: str) -> List[str]:
        """
        Generate all possible variations of a name for database searching
        
        Args:
            input_name: The name as entered by user
            
        Returns:
            List of name variations to try in database queries
        """
        variations = []
        
        # Original name
        variations.append(input_name.strip())
        
        # With different cases
        variations.append(input_name.strip().title())
        variations.append(input_name.strip().upper()) 
        variations.append(input_name.strip().lower())
        
        # Replace spaces with hyphens
        if ' ' in input_name:
            variations.append(input_name.replace(' ', '-'))
            variations.append(input_name.replace(' ', '-').title())
        
        # Replace hyphens with spaces  
        if '-' in input_name:
            variations.append(input_name.replace('-', ' '))
            variations.append(input_name.replace('-', ' ').title())
        
        # Remove all punctuation
        clean_name = re.sub(r'[^\w\s]', ' ', input_name)
        clean_name = ' '.join(clean_name.split())  # Normalize spaces
        if clean_name not in variations:
            variations.append(clean_name)
            variations.append(clean_name.title())
        
        # For Swedish/international names, try without accents
        normalized = self.normalize_name(input_name)
        if normalized not in [self.normalize_name(v) for v in variations]:
            variations.append(normalized)
            variations.append(normalized.title())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for var in variations:
            if var and var not in seen:
                seen.add(var)
                unique_variations.append(var)
        
        return unique_variations
    
    def fuzzy_match_score(self, input_name: str, db_name: str) -> float:
        """
        Calculate fuzzy match score between input name and database name
        
        Returns:
            Float between 0.0 (no match) and 1.0 (perfect match)
        """
        if not input_name or not db_name:
            return 0.0
        
        # Normalize both names
        norm_input = self.normalize_name(input_name)
        norm_db = self.normalize_name(db_name)
        
        # Exact match after normalization
        if norm_input == norm_db:
            return 1.0
        
        # Check if one contains the other (for partial matches)
        if norm_input in norm_db or norm_db in norm_input:
            return 0.8
        
        # Word-by-word matching for multi-word names
        input_words = set(norm_input.split())
        db_words = set(norm_db.split())
        
        if input_words and db_words:
            intersection = len(input_words.intersection(db_words))
            union = len(input_words.union(db_words))
            
            if union > 0:
                jaccard_score = intersection / union
                # Boost score if all input words are found
                if input_words.issubset(db_words):
                    jaccard_score += 0.2
                return min(jaccard_score, 1.0)
        
        return 0.0
    
    def find_best_matches(self, input_name: str, candidates: List[Dict[str, Any]], 
                         name_field: str = 'name', threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Find best matching names from a list of candidates
        
        Args:
            input_name: Name to search for
            candidates: List of dicts containing candidate names
            name_field: Field name containing the name in each candidate dict
            threshold: Minimum score threshold for matches
            
        Returns:
            List of candidates sorted by match score (best first)
        """
        scored_candidates = []
        
        for candidate in candidates:
            db_name = candidate.get(name_field, '')
            if not db_name:
                continue
                
            score = self.fuzzy_match_score(input_name, db_name)
            
            if score >= threshold:
                candidate_copy = candidate.copy()
                candidate_copy['_match_score'] = score
                scored_candidates.append(candidate_copy)
        
        # Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x['_match_score'], reverse=True)
        
        return scored_candidates


def test_name_matching():
    """Test the enhanced name matching system"""
    matcher = EnhancedNameMatcher()
    
    print(" TESTING ENHANCED NAME MATCHING")
    print("=" * 50)
    
    # Test name normalization
    test_names = [
        "Per-Olof Arnäs",
        "Per Olof Arnas", 
        "PER-OLOF ARNÄS",
        "per olof arnäs",
        "María José González",
        "Maria Jose Gonzalez",
        "O'Brien",
        "OBrien"
    ]
    
    print(" Name Normalization Test:")
    for name in test_names:
        normalized = matcher.normalize_name(name)
        print(f"   '{name}' → '{normalized}'")
    
    print(f"\n Variation Generation Test:")
    input_name = "Per Olof Arnäs"
    variations = matcher.generate_name_variations(input_name)
    print(f"Input: '{input_name}'")
    print("Variations:")
    for i, var in enumerate(variations, 1):
        print(f"   {i}. '{var}'")
    
    print(f"\n Fuzzy Matching Test:")
    test_pairs = [
        ("Per Olof Arnäs", "Per-Olof Arnäs"),
        ("Maria Elena", "María-Elena González"),
        ("John Smith", "J. Smith"),
        ("Anders", "Anders Andersson"),
        ("José", "Jose")
    ]
    
    for input_name, db_name in test_pairs:
        score = matcher.fuzzy_match_score(input_name, db_name)
        print(f"   '{input_name}' vs '{db_name}' → {score:.2f}")


if __name__ == "__main__":
    test_name_matching()