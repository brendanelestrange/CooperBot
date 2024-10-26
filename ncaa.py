#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 23:10:10 2024

@author: brendan
"""
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
headers = {'User-Agent': 'Mozilla/5.0'}

url_ncaa = "https://www.ncaa.com/rankings/basketball-men/d1/ncaa-mens-basketball-net-rankings"
response_ncaa = requests.get(url_ncaa, headers=headers)
soup_ncaa = BeautifulSoup(response_ncaa.text, 'html.parser')

# Lists for NCAA data
ncaa_data = []
for row in soup_ncaa.find_all('tr')[1:]:
    cols = row.find_all('td')
    if len(cols) >= 12:
        rank_ncaa = cols[0].text.strip()
        team = cols[2].text.strip()
        road = cols[5].text.strip()
        neutral = cols[6].text.strip()
        home = cols[7].text.strip()
        quads = [col.text.strip() for col in cols[8:12]]
        ncaa_data.append([team, rank_ncaa, road, neutral, home] + quads)

# Create DataFrame for NCAA data
ncaa_df = pd.DataFrame(ncaa_data, columns=["Team", "NCAA Rank", "Road", "Neutral", "Home", "Quad1", "Quad2", "Quad3", "Quad4"])

os.makedirs("results", exist_ok=True)
ncaa_df.to_csv('results/ncaa.csv', index=False)
print("saved to ncaa.csv")