#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Combined Basketball Rankings Script
Combines rankings from multiple sources
"""

import time
import requests
import pandas as pd
import re
from typing import Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from team_name_standardizer import EnhancedTeamNameStandardizer

class BasketballRankingsParser:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        self.team_name_standardizer = EnhancedTeamNameStandardizer()

    def standardize_team_name(self, team_name: str) -> str:
        """Standardize team names using the EnhancedTeamNameStandardizer."""
        return self.team_name_standardizer.clean_name(team_name)

    def clean_text(self, text: str) -> str:
        """Remove HTML tags and clean up the text."""
        clean = re.sub(r'<[^>]+>', '', text)
        clean = re.sub(r'\[.*?\]', '', clean)
        return clean.strip()

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
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
            # Navigate to ESPN BPI page
            espn_url = "https://www.espn.com/mens-college-basketball/bpi"
            driver.get(espn_url)
            
            # Click "Load More" until all teams are loaded
            while True:
                try:
                    show_more_button = driver.find_element(By.CLASS_NAME, "loadMore__link")
                    show_more_button.click()
                    time.sleep(.3)  # Wait for more content to load
                except NoSuchElementException:
                    break
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()
            
            # Initialize data collection
            team_names = []
            bpi_data = []
            
            # Extract team names and BPI data
            for row in soup.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) == 2:  # Rows with team names
                    team_name = self.standardize_team_name(cols[0].text.strip())
                    team_names.append(team_name)
                elif len(cols) >= 7:  # Rows with BPI data
                    bpi_rating = cols[1].text.strip()
                    bpi_rank = cols[2].text.strip()
                    bpi_data.append([bpi_rating, bpi_rank])
            
            # Combine data into DataFrame
            if len(team_names) == len(bpi_data):
                espn_data = [
                    [team_names[i]] + bpi_data[i][:] for i in range(len(team_names))
                ]
                espn_df = pd.DataFrame(espn_data, columns=["Team", "BPI Rating", "BPI Rank"])
                return espn_df.sort_values('BPI Rank').reset_index(drop=True)
                
            return pd.DataFrame(columns=["Team", "BPI Rating", "BPI Rank"])
            
        except Exception as e:
            print(f"Error getting ESPN rankings: {str(e)}")
            return pd.DataFrame(columns=["Team", "BPI Rating", "BPI Rank"])

def main():
    parser = BasketballRankingsParser()
    
    print("Fetching rankings from multiple sources...")
    
    # Get rankings from each source
    kenpom_df = parser.get_kenpom_rankings()
    ncaa_df = parser.get_ncaa_rankings()
    rpi_df = parser.get_rpi_rankings()
    sos_df = parser.get_sos_rankings()
    espn_df = parser.get_espn_rankings()
    
    # Save individual rankings
    kenpom_df.to_csv('results/kenpom.csv', index=False)
    ncaa_df.to_csv('results/ncaa.csv', index=False)
    rpi_df.to_csv('results/rpi.csv', index=False)
    sos_df.to_csv('results/sos.csv', index=False)
    espn_df.to_csv('results/espn_normalized.csv', index=False)
    
    print("\nCombining rankings...")
    
    # Merge all DataFrames
    dfs = [kenpom_df, ncaa_df, rpi_df, sos_df, espn_df]
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