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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from concurrent.futures import ThreadPoolExecutor


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
    
    def fetch_all_rankings(self):
        """Fetch all rankings in parallel using multithreading."""
        with ThreadPoolExecutor() as executor:
            # Define tasks for fetching data
            tasks = {
                "kenpom": executor.submit(self.get_kenpom_rankings),
                "ncaa": executor.submit(self.get_ncaa_rankings),
                "rpi": executor.submit(self.get_rpi_rankings),
                "sos": executor.submit(self.get_sos_rankings),
                "espn": executor.submit(self.get_espn_rankings)
            }

            # Collect results as they are completed
            results = {}
            for source, task in tasks.items():
                try:
                    results[source] = task.result()  # Get the result of each task
                except Exception as e:
                    print(f"Error fetching {source} rankings: {e}")
                    results[source] = pd.DataFrame()  # Empty DataFrame on failure

        return results


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
            # Set up Selenium WebDriver
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
            # Navigate to ESPN BPI page
            espn_url = "https://www.espn.com/mens-college-basketball/bpi"
            driver.get(espn_url)

            # Use WebDriverWait for the "Load More" button to minimize sleep
            while True:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "loadMore__link"))
                    ).click()
                except TimeoutException:
                    # Exit loop when no "Load More" button is found
                    break

            # Parse the page with BeautifulSoup
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

            # Return an empty DataFrame if there's a mismatch
            return pd.DataFrame(columns=["Team", "BPI Rating", "BPI Rank"])

        except Exception as e:
            print(f"Error getting ESPN rankings: {str(e)}")
            return pd.DataFrame(columns=["Team", "BPI Rating", "BPI Rank"])


def main():
    parser = BasketballRankingsParser()
    print("Fetching rankings from multiple sources...")

    # Fetch all rankings in parallel
    rankings = parser.fetch_all_rankings()

    # Save individual rankings
    for source, df in rankings.items():
        if not df.empty:
            output_path = f"results/{source}.csv"
            df.to_csv(output_path, index=False)
            print(f"{source.capitalize()} rankings saved to {output_path}")
        else:
            print(f"Failed to fetch {source.capitalize()} rankings.")

    print("\nCombining rankings...")

    # Combine all fetched rankings into a single DataFrame
    combined_df = None
    for df in rankings.values():
        if combined_df is None:
            combined_df = df
        else:
            combined_df = pd.merge(combined_df, df, on="Team", how="inner")

    if combined_df is not None and not combined_df.empty:
        combined_df.to_csv('combined_rankings.csv', index=False)
        print(f"\nProcessed {len(combined_df)} teams across all rankings")
        print("All rankings have been saved to combined_rankings.csv")
    else:
        print("No rankings to combine.")

    # Identify unmatched teams
    all_teams = set()
    for df in rankings.values():
        if not df.empty:
            all_teams.update(df['Team'].unique())

    matched_teams = set(combined_df['Team'].unique()) if combined_df is not None else set()
    unmatched_teams = all_teams - matched_teams

    if unmatched_teams:
        print("\nTeams that didn't match across all sources:")
        for team in sorted(unmatched_teams):
            print(f"  {team}")

if __name__ == "__main__":
    main()