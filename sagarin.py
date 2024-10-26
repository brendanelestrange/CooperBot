#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import pandas as pd
import re
from typing import Optional, Dict
import os

class BasketballRankingsParser:
    def __init__(self):
        # Updated pattern to exclude conference entries
        self.team_pattern = re.compile(
            r'^\s*(\d+)\s+(?!ACC|BIG TEN|WEST COAST|CONFERENCE USA|MISSOURI VALLEY|SOUTHWESTERN|BIG WEST|ATLANTIC SUN|HORIZON|NORTHEAST|INDEPENDENTS|MOUNTAIN WEST|ATLANTIC COAST|SOUTHLAND|OHIO VALLEY|IVY LEAGUE|WESTERN ATHLETIC|SOUTHERN|BIG SKY|METRO ATLANTIC|BIG SOUTH|COLONIAL|SUMMIT LEAGUE|AMERICA EAST|PATRIOT|AMER. ATHLETIC|SOUTHEASTERN|BIG EAST|BIG 12|SEC|PAC 12|AAC|MWC|WCC|MVC|CAA|CUSA|MAC|SUN BELT|WAC)([A-Za-z][A-Za-z. \'\-&()]+?)\s+=?\s+([\d.]+)'
        )
        
        # Define known conference names for filtering
        self.conferences = {
            'ACC', 'BIG TEN', 'BIG EAST', 'BIG 12', 'SEC', 'PAC 12',
            'AAC', 'MWC', 'WCC', 'MVC', 'CAA', 'CUSA', 'MAC',
            'SUN BELT', 'WAC'
        }

    def is_conference(self, name: str) -> bool:
        """Check if the given name is a conference name."""
        return name.strip().upper() in {conf.upper() for conf in self.conferences}

    def clean_text(self, text: str) -> str:
        """Remove HTML tags and clean up the text."""
        clean = re.sub(r'<[^>]+>', '', text)
        clean = re.sub(r'\[.*?\]', '', clean)
        return clean.strip()

    def parse_team_line(self, line: str) -> Optional[Dict]:
        """Parse a team entry line for rank, team, and rating only."""
        match = self.team_pattern.match(line)
        if match:
            team_name = match.group(2).strip()
            # Double-check that it's not a conference name
            if not self.is_conference(team_name):
                return {
                    'Rank': int(match.group(1)),
                    'Team': team_name,
                    'Rating': float(match.group(3))
                }
        return None

    def parse_rankings(self, url: str) -> Optional[pd.DataFrame]:
        """Parse basketball rankings from the given URL."""
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            lines = response.text.splitlines()
            cleaned_lines = [self.clean_text(line) for line in lines]
            
            teams_data = []
            seen_teams = set()
            
            for line in cleaned_lines:
                if not line.strip() or '_' in line or 'FINAL' in line:
                    continue
                
                team_data = self.parse_team_line(line)
                if team_data:
                    team_name = team_data['Team']
                    if team_name not in seen_teams:
                        teams_data.append(team_data)
                        seen_teams.add(team_name)
            
            # Create DataFrame
            if teams_data:
                teams_df = pd.DataFrame(teams_data)
                teams_df = teams_df.sort_values('Rank').reset_index(drop=True)
                
                # Print summary
                print(f"\nTotal teams processed: {len(teams_df)}")
                print("\nFirst few teams:")
                print(teams_df.head())
                
                return teams_df
            
            return None
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return None

def main():
    url = "http://sagarin.com/sports/cbsend.htm"
    parser = BasketballRankingsParser()
    
    teams_df = parser.parse_rankings(url)
    
    if teams_df is not None:
        os.makedirs("results", exist_ok=True)
        teams_df.to_csv('results/sagarin.csv', index=False)
        print("\nData saved to sagarin.csv")

if __name__ == "__main__":
    main()