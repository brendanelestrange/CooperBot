#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Team Name Standardizer
Standardizes college basketball team names across different ranking sources
"""

import re
from typing import Set, Dict, List, Optional
from difflib import SequenceMatcher

class EnhancedTeamNameStandardizer:
    def __init__(self):
        # Core mappings for team names
        self.name_mappings = {
            # State Universities
            "Iowa State": "Iowa St.",
            "Michigan State": "Michigan St.",
            "Ohio State": "Ohio St.",
            "Oklahoma State": "Oklahoma St.",
            "Oregon State": "Oregon St.",
            "Washington State": "Washington St.",
            "Colorado State": "Colorado St.",
            "Florida State": "Florida St.",
            "Kansas State": "Kansas St.",
            "Mississippi State": "Mississippi St.",
            "Penn State": "Penn St.",
            "San Diego State": "San Diego St.",
            "San Jose State": "San Jose St.",
            "Arizona State": "Arizona St.",
            "Arkansas State": "Arkansas St.",
            "Boise State": "Boise St.",
            "Fresno State": "Fresno St.",
            "Idaho State": "Idaho St.",
            "Illinois State": "Illinois St.",
            "Indiana State": "Indiana St.",
            "Kent State": "Kent St.",
            "Montana State": "Montana St.",
            "Sacramento State": "Sacramento St.",
            "Utah State": "Utah St.",
            "Weber State": "Weber St.",
            "Wright State": "Wright St.",
            
            # Common Abbreviations
            "Louisiana State": "LSU",
            "Texas Christian": "TCU",
            "Southern California": "USC",
            "Central Florida": "UCF",
            "Connecticut": "UConn",
            "Nevada-Las Vegas": "UNLV",
            "Virginia Military": "VMI",
            "Virginia Military Institute": "VMI",
            "Texas A&M-Corpus Christi": "Texas A&M CC",
            "Texas A&M Corpus Christi": "Texas A&M CC",
            "TX A&M CC": "Texas A&M CC",
            "Maryland-Baltimore County": "UMBC",
            "Brigham Young": "BYU",
            "Virginia Tech": "VA Tech",
            "Georgia Tech": "GA Tech",
            "Louisiana Tech": "LA Tech",
            "Texas Tech": "Texas Tech",
            
            # California State System
            "Cal State Fullerton": "CS Fullerton",
            "Cal State Northridge": "CS Northridge",
            "Cal State Bakersfield": "CS Bakersfield",
            "California Baptist": "Cal Baptist",
            "California Davis": "UC Davis",
            "California Irvine": "UC Irvine",
            "California Riverside": "UC Riverside",
            "California Santa Barbara": "UC Santa Barbara",
            
            # North Carolina System
            "North Carolina State": "NC State",
            "North Carolina Central": "NC Central",
            "North Carolina A&T": "NC A&T",
            "UNC Wilmington": "NC Wilmington",
            "UNC Greensboro": "NC Greensboro",
            "UNC Asheville": "NC Asheville",
            "North Carolina-Asheville": "NC Asheville",
            "North Carolina-Greensboro": "NC Greensboro",
            "North Carolina-Wilmington": "NC Wilmington",
            
            # South Carolina System
            "South Carolina State": "SC State",
            "South Carolina Upstate": "SC Upstate",
            
            # Other Common Cases
            "Southern Illinois Edwardsville": "SIU Edwardsville",
            "Missouri-Kansas City": "Kansas City",
            "UT Rio Grande Valley": "UTRGV",
            "Texas Rio Grande Valley": "UTRGV",
            "Maryland Eastern Shore": "MD Eastern Shore",
            "Alabama Birmingham": "UAB",
            "Louisiana Monroe": "UL Monroe",
            "Louisiana Lafayette": "UL Lafayette",
            "Prairie View A&M": "Prairie View",
            "Bethune Cookman": "Bethune-Cookman",
            "Texas Arlington": "UT Arlington",
            "Texas San Antonio": "UTSA",
            "Florida International": "FIU",
            "Florida Gulf Coast": "FGCU",
            "St. Francis PA": "St. Francis (PA)",
            "St. Francis NY": "St. Francis (NY)",
            "St. Francis Brooklyn": "St. Francis (NY)",
            "Mount Saint Mary's": "Mount St. Mary's",
            "Saint Mary's": "St. Mary's",
            "Saint Mary's (CA)": "St. Mary's",
            "Saint Joseph's": "St. Joseph's",
            "Saint Louis": "St. Louis",
            "Saint Peter's": "St. Peter's",
            "Saint John's": "St. John's",
            "Saint Bonaventure": "St. Bonaventure",
            "Saint Francis": "St. Francis",
        }
        
        # Common words to standardize
        self.word_standardization = {
            "University": "",
            "College": "",
            "State University": "State",
            "State College": "State",
            "-": " ",
            "Saint": "St.",
            "North Carolina": "NC",
            "Northern": "N.",
            "Southern": "S.",
            "Eastern": "E.",
            "Western": "W.",
            "Central": "C.",
            "Florida": "Fla.",
            "Carolina": "Car.",
            "Arkansas": "Ark.",
            "Mississippi": "Miss.",
        }
        
        # Common patterns to standardize
        self.patterns = {
            r'St\.?$': 'St.',  # Standardize State abbreviation
            r'([A-Z])\s*&\s*([A-Z])': r'\1&\2',  # Standardize A&M format
            r'\s+': ' ',  # Standardize spaces
            r'(\w+)\s*\(\s*(\w+)\s*\)': r'\1 \2',  # Remove parentheses
            r'[()]': '',  # Remove remaining parentheses
            r'\s*-\s*': '-',  # Standardize hyphens
        }
        
        # Build reverse mappings for lookups
        self.build_reverse_mappings()

    def build_reverse_mappings(self) -> None:
        """Build reverse mappings for team name lookups."""
        self.reverse_mappings = {}
        for original, standardized in self.name_mappings.items():
            if standardized not in self.reverse_mappings:
                self.reverse_mappings[standardized] = set()
            self.reverse_mappings[standardized].add(original)
            # Add variations with common substitutions
            for pattern, replacement in self.word_standardization.items():
                variant = original.replace(pattern, replacement).strip()
                if variant != original:
                    self.reverse_mappings[standardized].add(variant)

    def clean_name(self, name: str) -> str:
        """
        Clean and standardize a team name.
        
        Args:
            name: Raw team name string
            
        Returns:
            Standardized team name string
        """
        if not name:
            return name
            
        # Initial cleanup
        name = name.strip()
        
        # Direct mapping lookup
        if name in self.name_mappings:
            return self.name_mappings[name]
        
        # Remove anything in parentheses unless it's a state identifier
        name = re.sub(r'\s*\([^)]*\)', '', name)
        
        # Apply patterns
        for pattern, replacement in self.patterns.items():
            name = re.sub(pattern, replacement, name)
        
        # Apply word standardization
        words = name.split()
        standardized_words = []
        i = 0
        while i < len(words):
            # Try to match multiple word phrases first
            matched = False
            for j in range(min(4, len(words) - i + 1), 0, -1):
                phrase = ' '.join(words[i:i+j])
                if phrase in self.word_standardization:
                    replacement = self.word_standardization[phrase]
                    if replacement:
                        standardized_words.append(replacement)
                    i += j
                    matched = True
                    break
            if not matched:
                standardized_words.append(words[i])
                i += 1
        
        name = ' '.join(w for w in standardized_words if w)
        
        # Clean up extra spaces and standardize St./State
        name = re.sub(r'\s+', ' ', name).strip()
        if name.endswith(" St"):
            name = name.replace(" St", " St.")
            
        return name

    def get_variations(self, name: str) -> Set[str]:
        """
        Generate common variations of a team name.
        
        Args:
            name: Team name string
            
        Returns:
            Set of possible variations of the team name
        """
        variations = {name}
        
        # Add standard variations
        clean_name = self.clean_name(name)
        variations.add(clean_name)
        
        # Add reverse mappings if available
        if clean_name in self.reverse_mappings:
            variations.update(self.reverse_mappings[clean_name])
        
        # Generate additional variations
        for variant in list(variations):
            # Add version with/without periods
            if "." in variant:
                variations.add(variant.replace(".", ""))
            else:
                name_with_periods = variant
                for abbrev in ["St", "Univ"]:
                    if name_with_periods.endswith(f" {abbrev}"):
                        name_with_periods = name_with_periods.replace(f" {abbrev}", f" {abbrev}.")
                variations.add(name_with_periods)
            
            # Add versions with different separators
            if "-" in variant:
                variations.add(variant.replace("-", " "))
            if " " in variant:
                variations.add(variant.replace(" ", "-"))
        
        return variations

    def find_closest_match(self, name: str, candidates: List[str], threshold: float = 0.85) -> Optional[str]:
        """
        Find the closest matching team name from a list of candidates.
        
        Args:
            name: Team name to match
            candidates: List of possible team names to match against
            threshold: Minimum similarity score to consider a match
            
        Returns:
            Best matching team name or None if no good match found
        """
        clean_name = self.clean_name(name)
        variations = self.get_variations(clean_name)
        
        best_match = None
        best_score = 0
        
        for candidate in candidates:
            candidate_clean = self.clean_name(candidate)
            candidate_variations = self.get_variations(candidate_clean)
            
            for var1 in variations:
                for var2 in candidate_variations:
                    score = SequenceMatcher(None, var1.lower(), var2.lower()).ratio()
                    if score > best_score:
                        best_score = score
                        best_match = candidate
        
        return best_match if best_score >= threshold else None

    def are_same_team(self, name1: str, name2: str) -> bool:
        """
        Check if two team names refer to the same team.
        
        Args:
            name1: First team name
            name2: Second team name
            
        Returns:
            True if names likely refer to the same team, False otherwise
        """
        variations1 = self.get_variations(self.clean_name(name1))
        variations2 = self.get_variations(self.clean_name(name2))
        return bool(variations1.intersection(variations2))

def main():
    """Test the team name standardizer with some examples."""
    standardizer = EnhancedTeamNameStandardizer()
    
    test_names = [
        "North Carolina State",
        "NC State",
        "N.C. State",
        "North Carolina St",
        "Michigan State University",
        "Michigan St.",
        "Michigan St",
        "UNC-Wilmington",
        "UNC Wilmington",
        "North Carolina-Wilmington",
        "Saint Mary's (CA)",
        "Saint Mary's California",
        "St. Mary's",
        "Texas A&M Corpus Christi",
        "Texas A&M-Corpus Christi",
        "Texas A&M CC"
    ]
    
    print("Testing team name standardization:")
    for name in test_names:
        standardized = standardizer.clean_name(name)
        print(f"{name:40} -> {standardized}")
        
    print("\nTesting variation generation:")
    variations = standardizer.get_variations("North Carolina State")
    print("Variations for 'North Carolina State':")
    for var in sorted(variations):
        print(f"  {var}")
        
    print("\nTesting team name matching:")
    pairs = [
        ("Michigan State", "Michigan St."),
        ("UNC-Wilmington", "North Carolina Wilmington"),
        ("Saint Mary's (CA)", "St. Mary's California"),
        ("Texas A&M CC", "Texas A&M-Corpus Christi")
    ]
    
    for name1, name2 in pairs:
        result = standardizer.are_same_team(name1, name2)
        print(f"'{name1}' and '{name2}' are{' ' if result else ' not '}the same team")

if __name__ == "__main__":
    main()
