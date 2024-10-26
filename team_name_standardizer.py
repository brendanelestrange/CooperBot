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
        # Core mappings for team names (including newly added names)
        self.name_mappings = {

            "A&M-Corpus Christi": "Texas A&M Corpus Christi",
            "AR Lit Rock": "Arkansas Little Rock",
            "Abl Christian": "Abilene Christian",
            "Ala.": "Alabama",
            "Ala. St.": "Alabama State",
            "Alab A&M": "Alabama A&M",
            "Albany-NY": "Albany",
            "Alcorn": "Alcorn State",
            "American U.": "American",
            "App St.": "Appalachian State",
            "Appalachian St.": "Appalachian State",
            "Ark Pine Bl": "Arkansas Pine Bluff",
            "Ark.-Pine Bluff": "Arkansas Pine Bluff",
            "Army West Point": "Army",

            "Abilene Christian": "Abilene Christian",
            "Air Force": "Air Force",
            "Akron": "Akron",
            "Ala. St.": "Alabama State",
            "Alabama A&M": "Alabama A&M",
            "Alabama State": "Alabama State",
            "Albany": "Albany",
            "Alcorn St.": "Alcorn State",
            "Alcorn State": "Alcorn State",
            "American": "American",
            "Appalachian State": "Appalachian State",
            "Arizona St.": "Arizona State",
            "Arizona State": "Arizona State",
            "Arkansas": "Arkansas",
            "Arkansas Pine Bluff": "Arkansas Pine Bluff",
            "Arkansas St.": "Arkansas State",
            "Arkansas State": "Arkansas State",
            "Army": "Army",
            "Austin Peay": "Austin Peay",
            "BYU": "Brigham Young",

            "Beth-Cook": "Bethune-Cookman",
            "Boise St": "Boise State",
            "Boise St.": "Boise State",
            "Boston": "Boston University",

            "Ball St.": "Ball State",
            "Ball State": "Ball State",
            "Bellarmine": "Bellarmine",
            "Belmont": "Belmont",
            "Bethune Cookman": "Bethune-Cookman",
            "Bethune-Cookman": "Bethune-Cookman",
            "Binghamton": "Binghamton",
            "Binghamton-NY": "Binghamton",
            "Boise St": "Boise State",
            "Boise St.": "Boise State",
            "Boston": "Boston University",
            "Boston Col": "Boston College",
            "Boston U": "Boston University",
            "Boston U.": "Boston University",
            "Bowling Green": "Bowling Green",
            "Bowling Grn": "Bowling Green",
            "Bradley": "Bradley",
            "Brigham Young": "Brigham Young",
            "Brown": "Brown",
            "Bryant": "Bryant",
            "Bucknell": "Bucknell",
            "Buffalo": "Buffalo",
            "Butler": "Butler",
            "C. Ark": "Central Arkansas",

            "C. Ark.": "Central Arkansas",
            "C. Arkansas": "Central Arkansas",
            "C. Conn": "Central Connecticut",
            "C. Conn. St.": "Central Connecticut",
            "C. Connecticut": "Central Connecticut",
            "C. Connecticut St.": "Central Connecticut",
            "C. Fla.": "Central Florida",
            "C. Mich": "Central Michigan",
            "C. Mich.": "Central Michigan",
            "C. Michigan": "Central Michigan",
            "CS Bakersfield": "Cal State Bakersfield",
            "CS Bakersfld": "Cal State Bakersfield",
            "CS Fullerton": "Cal State Fullerton",
            "CS Northridge": "Cal State Northridge",
            "CSU Bakersfield": "Cal State Bakersfield",
            "CSUN": "Cal State Northridge",
            "Cal Baptist": "California Baptist",
            "Cal Poly": "California Polytechnic",
            "Cal Poly-SLO": "California Polytechnic",
            "Cal St Nrdge": "Cal State Northridge",
            "Cal St. Bakersfield": "Cal State Bakersfield",
            "Cal St. Fullerton": "Cal State Fullerton",
            "California": "California",
            "California Baptist": "California Baptist",
            "Campbell": "Campbell",
            "Canisius": "Canisius",
            "Charl South": "Charleston Southern",
            "Charleston": "Charleston",
            "Charleston S.": "Charleston Southern",
            "Charleston So.": "Charleston Southern",
            "Charlotte": "Charlotte",
            "Chattanooga": "Chattanooga",
            "Chicago St.": "Chicago State",
            "Citadel": "The Citadel",
            "Cleveland St.": "Cleveland State",
            "Coastal Car": "Coastal Carolina",
            "Coastal Car.": "Coastal Carolina",
            "Col Charlestn": "College of Charleston",
            "Col. of Charleston": "College of Charleston",
            "Colgate": "Colgate",
            "Colorado St.": "Colorado State",
            "Columbia": "Columbia",
            "Connecticut": "UConn",
            "Coppin St.": "Coppin State",
            "Cornell": "Cornell",
            "Dartmouth": "Dartmouth",
            "Davidson": "Davidson",
            "DePaul": "DePaul",
            "Delaware": "Delaware",
            "Delaware St.": "Delaware State",
            "Denver": "Denver",
            "Detroit": "Detroit Mercy",
            "Detroit Mercy": "Detroit Mercy",
            "Drake": "Drake",
            "Drexel": "Drexel",
            "Duquesne": "Duquesne",
            "E Car.": "East Carolina",
            "E Illinois": "Eastern Illinois",
            "E Kentucky": "Eastern Kentucky",
            "E Michigan": "Eastern Michigan",
            "E Tenn St.": "East Tennessee State",
            "E Washingtn": "Eastern Washington",
            "E. Ill.": "Eastern Illinois",
            "E. Illinois": "Eastern Illinois",
            "E. Kentucky": "Eastern Kentucky",
            "E. Ky.": "Eastern Kentucky",
            "E. Mich.": "Eastern Michigan",
            "E. Michigan": "Eastern Michigan",
            "E. Wash.": "Eastern Washington",
            "E. Washington": "Eastern Washington",
            "ETSU": "East Tennessee State",
            "East Car.": "East Carolina",
            "East Tennessee St.": "East Tennessee State",
            "Elon": "Elon",
            "Evansville": "Evansville",
            "F Dickinson": "Fairleigh Dickinson",
            "FDU": "Fairleigh Dickinson",
            "FGCU": "Florida Gulf Coast",
            "FIU": "Florida International",
            "Fairfield": "Fairfield",
            "Fairleigh Dickinson": "Fairleigh Dickinson",
            "Fla Atlantic": "Florida Atlantic",
            "Fla Gulf Cst": "Florida Gulf Coast",
            "Fla.": "Florida",
            "Fla. A&M": "Florida A&M",
            "Fla. Atlantic": "Florida Atlantic",
            "Fla. Gulf Coast": "Florida Gulf Coast",
            "Fla. International": "Florida International",
            "Fla. Intl": "Florida International",
            "Fla. St.": "Florida State",
            "Florida": "Florida",
            "Fordham": "Fordham",
            "Fort Wayne": "Purdue Fort Wayne",
            "Fresno St.": "Fresno State",
            "Furman": "Furman",
            "GA S.": "Georgia Southern",
            "GA Tech": "Georgia Tech",
            "Ga.": "Georgia",
            "Ga. S.": "Georgia Southern",
            "Ga. St.": "Georgia State",
            "Ga. Tech": "Georgia Tech",
            "Gard-Webb": "Gardner-Webb",
            "Gardner Webb": "Gardner-Webb",
            "Gardner-Webb": "Gardner-Webb",
            "Geo Mason": "George Mason",
            "Geo Wshgtn": "George Washington",
            "George Mason": "George Mason",
            "George Washington": "George Washington",
            "Georgetown": "Georgetown",
            "Grambling": "Grambling State",
            "Grambling St.": "Grambling State",
            "Grand Canyon": "Grand Canyon",
            "Grd Canyon": "Grand Canyon",
            "Green Bay": "Green Bay",
            "Hampton": "Hampton",
            "Hartford": "Hartford",
            "Harvard": "Harvard",
            "Hawai'i": "Hawaii",
            "Hawaii": "Hawaii",
            "High Point": "High Point",
            "Hofstra": "Hofstra",
            "Holy Cross": "Holy Cross",
            "Houston Christian": "Houston Christian",
            "Howard": "Howard",
            "Hsn Christian": "Houston Christian",
            "IL-Chicago": "Illinois Chicago",
            "IPFW": "Purdue Fort Wayne",
            "IU Indy": "IUPUI",
            "IUPUI": "IUPUI",
            "Idaho": "Idaho",
            "Idaho St.": "Idaho State",
            "Illinois Chicago": "Illinois Chicago",
            "Illinois St.": "Illinois State",
            "Illinois-Chicago": "Illinois Chicago",
            "Incar Word": "Incarnate Word",
            "Incarnate Word": "Incarnate Word",
            "Indiana": "Indiana",
            "Indiana St": "Indiana State",
            "Indiana St.": "Indiana State",
            "Iona": "Iona",
            "Iowa St": "Iowa State",
            "Iowa St.": "Iowa State",
            "Jackson St.": "Jackson State",
            "Jacksonville": "Jacksonville",
            "Jacksonville St.": "Jacksonville State",
            "James Mad": "James Madison",
            "James Madison": "James Madison",
            "Jksnville St.": "Jacksonville State",
            "Kansas City": "Kansas City",
            "Kansas St.": "Kansas State",
            "Kennesaw St.": "Kennesaw State",
            "Kent St.": "Kent State",
            "LA Tech": "Louisiana Tech",
            "LIU": "LIU Brooklyn",
            "LMU": "Loyola Marymount",
            "LSU": "Louisiana State",
            # Complete the mappings with all team names...
        }

        # Word standardizations to handle variations in naming conventions
        self.word_standardization = {
            "University": "",
            "College": "",
            "State": "St.",
            "-": " ",

            "Arkansas": "AR",
            "Little": "Lit",
            "Rock": "Rock",
            "Christian": "Christian",
            "University": "",
            "Point": "Pt",
            "Metropolitan": "Metro",
            "International": "Intl",
            "A&M": "A&M",
            "Saint": "St.",
            "Northern": "N.",
            "Southern": "S.",
            "Eastern": "E.",
            "Western": "W.",
            "Central": "C.",
            "Florida": "Fla.",
            "Carolina": "Car.",
            "Alabama": "Ala.",
            "Mississippi": "Miss.",
            "Georgia": "Ga.",
            "Texas": "TX",
        }

        # Patterns for specific replacements
        self.patterns = {
            r'St\.?$': 'St.',  # Standardize State abbreviation
            r'([A-Z])\s*&\s*([A-Z])': r'\1&\2',  # Standardize A&M format
            r'\s+': ' ',  # Standardize spaces
            r'(\w+)[\s-]NY$': r'\1',  # Remove -NY suffix
            r'West Point$': '',  # Remove West Point from Army
            r'[\s-]Metro$': ' Metropolitan',  # Standardize Metropolitan
            r'Lit[\s-]Rock': 'Little Rock',  # Standardize
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
                        name_with_periods = name_with_periods.replace(
                            f" {abbrev}", f" {abbrev}.")
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
                    score = SequenceMatcher(
                        None, var1.lower(), var2.lower()).ratio()
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
        print(f"'{name1}' and '{name2}' are{
              ' ' if result else ' not '}the same team")


if __name__ == "__main__":
    main()
