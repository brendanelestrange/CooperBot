#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 23:09:59 2024

@author: brendan
"""
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
headers = {'User-Agent': 'Mozilla/5.0'}
url_rpi = "https://www.teamrankings.com/ncb/rpi/"
response_rpi = requests.get(url_rpi, headers=headers)
soup_rpi = BeautifulSoup(response_rpi.text, 'html.parser')

# Lists for RPI data
rpi_data = []
for row in soup_rpi.find_all('tr')[1:]:
    cols = row.find_all('td')
    if len(cols) >= 5:
        rank_rpi = cols[0].text.strip()
        team_full = cols[1].text.strip()
        rating = cols[2].text.strip()
        
        # Strip the record from the team name
        team_name = team_full.split(' (')[0].strip()  # Get the team name before the parentheses
        rpi_data.append([team_name, rank_rpi, rating])

# Create DataFrame for RPI data outside the loop
rpi_df = pd.DataFrame(rpi_data, columns=["Team", "RPI Rank", "RPI Rating"])

os.makedirs("results", exist_ok=True)
rpi_df.to_csv('results/rpi.csv', index=False)