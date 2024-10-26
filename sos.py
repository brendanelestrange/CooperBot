#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 23:10:05 2024

@author: brendan
"""
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
headers = {'User-Agent': 'Mozilla/5.0'}

url_sos = "https://www.teamrankings.com/ncaa-basketball/ranking/schedule-strength-by-other"
response_sos = requests.get(url_sos, headers=headers)
soup_sos = BeautifulSoup(response_sos.text, 'html.parser')

sos_data = []
for row in soup_sos.find_all('tr')[1:]:
    cols = row.find_all('td')
    if len(cols) >= 5:
        sos_rank = cols[0].text.strip()
        team_full = cols[1].text.strip()
        sos_rating = cols[2].text.strip()
        
        team_name = team_full.split(' (')[0].strip() 
        sos_data.append([team_name, sos_rank, sos_rating])
        
sos_df = pd.DataFrame(sos_data, columns=["Team", "SOS Rank", "SOS Rating"])

os.makedirs("results", exist_ok=True)
sos_df.to_csv('results/sos.csv', index=False)
print("saved to results/sos.csv")