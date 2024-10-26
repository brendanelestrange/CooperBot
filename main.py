#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Combined Basketball Rankings Script
Combines functionality from sagarin.py, cooperbot.py, espn.py, kenpom.py, ncaa.py, rpi.py, and sos.py
with consistent team name handling
"""

import time
import requests
import pandas as pd
import re
from typing import Optional, Dict
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

class BasketballRankingsParser:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        # Updated Sagarin pattern to exclude conference entries
        self.team_pattern = re.compile(
            r'^\s*(\d+)\s+(?!ACC|BIG TEN|WEST COAST|CONFERENCE USA|MISSOURI VALLEY|SOUTHWESTERN|BIG WEST|ATLANTIC SUN|HORIZON|NORTHEAST|INDEPENDENTS|MOUNTAIN WEST|ATLANTIC COAST|SOUTHLAND|OHIO VALLEY|IVY LEAGUE|WESTERN ATHLETIC|SOUTHERN|BIG SKY|METRO ATLANTIC|BIG SOUTH|COLONIAL|SUMMIT LEAGUE|AMERICA EAST|PATRIOT|AMER. ATHLETIC|SOUTHEASTERN|BIG EAST|BIG 12|SEC|PAC 12|AAC|MWC|WCC|MVC|CAA|CUSA|MAC|SUN BELT|WAC)([A-Za-z][A-Za-z. \'\-&()]+?)\s+=?\s+([\d.]+)'
        )
        
        # Define known conference names for filtering Sagarin data
        self.conferences = {
            'ACC', 'BIG TEN', 'BIG EAST', 'BIG 12', 'SEC', 'PAC 12',
            'AAC', 'MWC', 'WCC', 'MVC', 'CAA', 'CUSA', 'MAC',
            'SUN BELT', 'WAC'
        }
        
        # ESPN-specific team mappings
        self.espn_mappings = {
            "Houston Cougars": "Houston",
            "UConn Huskies": "UConn",
            "Purdue Boilermakers": "Purdue",
            "Auburn Tigers": "Auburn",
            "Iowa State Cyclones": "Iowa St",
            "Arizona Wildcats": "Arizona",
            "Tennessee Volunteers": "Tennessee",
            "Duke Blue Devils": "Duke",
            "North Carolina Tar Heels": "N Carolina",
            "Creighton Bluejays": "Creighton",
            "Illinois Fighting Illini": "Illinois",
            "Alabama Crimson Tide": "Alabama",
            "Marquette Golden Eagles": "Marquette",
            "Baylor Bears": "Baylor",
            "Gonzaga Bulldogs": "Gonzaga",
            "Saint Mary's Gaels": "St Marys",
            "Michigan State Spartans": "Michigan St",
            "BYU Cougars": "BYU",
            "Wisconsin Badgers": "Wisconsin",
            "Clemson Tigers": "Clemson",
            "Kansas Jayhawks": "Kansas",
            "Texas Longhorns": "Texas",
            "St. John's Red Storm": "St Johns",
            "Kentucky Wildcats": "Kentucky",
            "Florida Gators": "Florida",
            "Texas Tech Red Raiders": "Texas Tech",
            "Pittsburgh Panthers": "Pittsburgh",
            "Texas A&M Aggies": "Texas A&M",
            "Dayton Flyers": "Dayton",
            "Cincinnati Bearcats": "Cincinnati",
            "Wake Forest Demon Deacons": "Wake Forest",
            "Villanova Wildcats": "Villanova",
            "TCU Horned Frogs": "TX Christian",
            "Mississippi State Bulldogs": "Miss State",
            "San Diego State Aztecs": "San Diego St",
            "Florida Atlantic Owls": "Fla Atlantic",
            "Nebraska Cornhuskers": "Nebraska",
            "Oklahoma Sooners": "Oklahoma",
            "Northwestern Wildcats": "Northwestern",
            "Indiana State Sycamores": "Indiana St",
            "NC State Wolfpack": "NC State",
            "Washington State Cougars": "Wash State",
            "Ohio State Buckeyes": "Ohio St",
            "Virginia Tech Hokies": "VA Tech",
            "Colorado Buffaloes": "Colorado",
            "Providence Friars": "Providence",
            "Iowa Hawkeyes": "Iowa",
            "Boise State Broncos": "Boise St",
            "New Mexico Lobos": "New Mexico",
            "Utah Utes": "Utah"
        }
        
        # Team name standardization mappings
        self.team_name_mappings = {
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
            "North Carolina State": "NC State",
            "Penn State": "Penn St.",
            "San Diego State": "San Diego St.",
            "San Jose State": "San Jose St.",
            
            # Other Universities
            "North Carolina": "UNC",
            "Southern California": "USC",
            "Connecticut": "UConn",
            "California Baptist": "Cal Baptist",
            "Louisiana State": "LSU",
            "Southern Methodist": "SMU",
            "Texas Christian": "TCU",
            "Virginia Military": "VMI",
            "Central Florida": "UCF",
            "Nevada-Las Vegas": "UNLV",
            "Maryland-Baltimore County": "UMBC",
            
            # Saints
            "Saint Mary's": "St. Mary's",
            "Saint John's": "St. John's",
            "Saint Joseph's": "St. Joseph's",
            "Saint Louis": "St. Louis",
            "Saint Peter's": "St. Peter's",
            "Saint Francis": "St. Francis",
            "Saint Bonaventure": "St. Bonaventure",
            
            # Directional Schools
            "Northern Illinois": "N Illinois",
            "Southern Illinois": "S Illinois",
            "Eastern Illinois": "E Illinois",
            "Western Illinois": "W Illinois",
            
            # Special Cases
            "Texas A&M": "Texas A&M",
            "Texas A&M-Corpus Christi": "Texas A&M-CC",
            "Virginia Tech": "Virginia Tech",
            "Texas Tech": "Texas Tech",
            "Louisiana Tech": "Louisiana Tech",
            "Georgia Tech": "Georgia Tech"
        }

    def is_conference(self, name: str) -> bool:
        """Check if the given name is a conference name."""
        return name.strip().upper() in {conf.upper() for conf in self.conferences}

    def standardize_team_name(self, team_name: str) -> str:
        """Standardize team names to ensure consistency across different sources."""
        # Check ESPN mappings first
        if team_name in self.espn_mappings:
            return self.espn_mappings[team_name]
            
        # Remove any trailing/leading whitespace and common suffixes
        clean_name = team_name.strip()
        clean_name = re.sub(r'\s*\([^)]*\)', '', clean_name)  # Remove anything in parentheses
        clean_name = re.sub(r'\s*University\s*$', '', clean_name)
        clean_name = re.sub(r'\s*College\s*$', '', clean_name)
        
        # Check direct mappings first
        if clean_name in self.team_name_mappings:
            return self.team_name_mappings[clean_name]
        
        return clean_name

    def clean_text(self, text: str) -> str:
        """Remove HTML tags and clean up the text."""
        clean = re.sub(r'<[^>]+>', '', text)
        clean = re.sub(r'\[.*?\]', '', clean)
        return clean.strip()

    def parse_sagarin_team_line(self, line: str) -> Optional[Dict]:
        """Parse a Sagarin team entry line."""
        match = self.team_pattern.match(line)
        if match:
            team_name = match.group(2).strip()
            # Double-check that it's not a conference name
            if not self.is_conference(team_name):
                return {
                    'Sagarin Rank': int(match.group(1)),
                    'Team': self.standardize_team_name(team_name),
                    'Sagarin Rating': float(match.group(3))
                }
        return None

    def get_sagarin_rankings(self, url: str) -> Optional[pd.DataFrame]:
        """Get Sagarin basketball rankings."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            lines = response.text.splitlines()
            cleaned_lines = [self.clean_text(line) for line in lines]
            
            teams_data = []
            seen_teams = set()
            
            for line in cleaned_lines:
                if not line.strip() or '_' in line or 'FINAL' in line:
                    continue
                
                team_data = self.parse_sagarin_team_line(line)
                if team_data:
                    team_name = team_data['Team']
                    if team_name not in seen_teams:
                        teams_data.append(team_data)
                        seen_teams.add(team_name)
            
            if teams_data:
                teams_df = pd.DataFrame(teams_data)
                return teams_df.sort_values('Sagarin Rank').reset_index(drop=True)
            
            return None
            
        except Exception as e:
            print(f"Error getting Sagarin rankings: {str(e)}")
            return None

    # [Rest of the class methods remain unchanged...]
    def get_kenpom_rankings(self) -> pd.DataFrame:
        """Get KenPom rankings."""
        url = "https://kenpom.com/index.php"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        teams, ranks, conference, win_loss, netrtg = [], [], [], [], []
        
        for row in soup.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 5:
                ranks.append(cols[0].text.strip())
                teams.append(self.standardize_team_name(cols[1].text.strip()))
                conference.append(cols[2].text.strip())
                win_loss.append(cols[3].text.strip())
                netrtg.append(cols[4].text.strip())
        
        return pd.DataFrame({
            'Team': teams,
            'KP Rank': ranks,
            'KP Conference': conference,
            'Win Loss': win_loss,
            'KP Net Rtg': netrtg
        })

    def get_ncaa_rankings(self) -> pd.DataFrame:
        """Get NCAA rankings."""
        url = "https://www.ncaa.com/rankings/basketball-men/d1/ncaa-mens-basketball-net-rankings"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        ncaa_data = []
        for row in soup.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 12:
                rank_ncaa = cols[0].text.strip()
                team = self.standardize_team_name(cols[2].text.strip())
                road = cols[5].text.strip()
                neutral = cols[6].text.strip()
                home = cols[7].text.strip()
                quads = [col.text.strip() for col in cols[8:12]]
                ncaa_data.append([team, rank_ncaa, road, neutral, home] + quads)
        
        return pd.DataFrame(ncaa_data, columns=[
            "Team", "NCAA Rank", "Road", "Neutral", "Home",
            "Quad1", "Quad2", "Quad3", "Quad4"
        ])

    def get_rpi_rankings(self) -> pd.DataFrame:
        """Get RPI rankings."""
        url = "https://www.teamrankings.com/ncb/rpi/"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rpi_data = []
        for row in soup.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 5:
                rank_rpi = cols[0].text.strip()
                team_full = cols[1].text.strip()
                rating = cols[2].text.strip()
                
                # Clean team name and standardize
                team_name = team_full.split(' (')[0].strip()
                team_name = self.standardize_team_name(team_name)
                rpi_data.append([team_name, rank_rpi, rating])
        
        return pd.DataFrame(rpi_data, columns=["Team", "RPI Rank", "RPI Rating"])

    def get_sos_rankings(self) -> pd.DataFrame:
        """Get Schedule Strength rankings."""
        url = "https://www.teamrankings.com/ncaa-basketball/ranking/schedule-strength-by-other"
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        sos_data = []
        for row in soup.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) >= 5:
                sos_rank = cols[0].text.strip()
                team_full = cols[1].text.strip()
                sos_rating = cols[2].text.strip()
                
                # Clean team name and standardize
                team_name = team_full.split(' (')[0].strip()
                team_name = self.standardize_team_name(team_name)
                sos_data.append([team_name, sos_rank, sos_rating])
        
        return pd.DataFrame(sos_data, columns=["Team", "SOS Rank", "SOS Rating"])

    def get_espn_rankings(self) -> pd.DataFrame:
        """Get ESPN BPI rankings with normalized team names."""
        try:
            # Read the saved ESPN CSV
            espn_df = pd.read_csv('espn.csv')
            
            # Normalize the team names using the ESPN mappings
            espn_df['Team'] = espn_df['Team'].map(self.espn_mappings)
            
            # Remove any rows where team name mapping wasn't found
            espn_df = espn_df.dropna(subset=['Team'])
            
            return espn_df
            
        except Exception as e:
            print(f"Error processing ESPN rankings: {str(e)}")
            return pd.DataFrame(columns=["Team", "BPI Rating", "BPI Rank"])

def main():
    parser = BasketballRankingsParser()
    
    print("Fetching rankings from multiple sources...")
    
    # Get rankings from each source
    sagarin_df = parser.get_sagarin_rankings("http://sagarin.com/sports/cbsend.htm")
    kenpom_df = parser.get_kenpom_rankings()
    ncaa_df = parser.get_ncaa_rankings()
    rpi_df = parser.get_rpi_rankings()
    sos_df = parser.get_sos_rankings()
    espn_df = parser.get_espn_rankings()
    
    # Save individual rankings
    sagarin_df.to_csv('sagarin.csv', index=False)
    kenpom_df.to_csv('kenpom.csv', index=False)
    ncaa_df.to_csv('ncaa.csv', index=False)
    rpi_df.to_csv('rpi.csv', index=False)
    sos_df.to_csv('sos.csv', index=False)
    espn_df.to_csv('espn_normalized.csv', index=False)  # Save normalized ESPN data
    
    print("\nCombining rankings...")
    
    # Merge all DataFrames
    dfs = [kenpom_df, ncaa_df, rpi_df, sos_df, espn_df]
    if sagarin_df is not None:
        dfs.append(sagarin_df)
    combined_df = dfs[0]
    for df in dfs[1:]:
        combined_df = pd.merge(combined_df, df, on="Team", how="inner")
    
    # Save combined rankings
    combined_df.to_csv('combined_rankings.csv', index=False)
    print(f"\nProcessed {len(combined_df)} teams across all rankings")
    print("All rankings have been saved to individual CSVs and combined_rankings.csv")
    
    # Print any teams that didn't match across all sources
    all_teams = set()
    for df in dfs:
        all_teams.update(df['Team'].unique())
    
    matched_teams = set(combined_df['Team'].unique())
    unmatched_teams = all_teams - matched_teams
    
    if unmatched_teams:
        print("\nTeams that didn't match across all sources:")
        for team in sorted(unmatched_teams):
            print(f"  {team}")

if __name__ == "__main__":
    main()