#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 23:10:24 2024

@author: brendan
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
headers = {'User-Agent': 'Mozilla/5.0'}
url_kp = "https://kenpom.com/index.php"

response_kp = requests.get(url_kp, headers=headers)
soup_kp = BeautifulSoup(response_kp.text, 'html.parser')

# Lists for KenPom data
teams, ranks, conference, win_loss, netrtg = [], [], [], [], []

for row in soup_kp.find_all('tr')[1:]:
    cols = row.find_all('td')
    if len(cols) >= 5:
        ranks.append(cols[0].text.strip())
        teams.append(cols[1].text.strip())
        conference.append(cols[2].text.strip())
        win_loss.append(cols[3].text.strip())
        netrtg.append(cols[4].text.strip())

# Create DataFrame for KenPom data
kenpom_df = pd.DataFrame({
    'Team': teams,
    'KP Rank': ranks,
    'KP Conference': conference,
    'Win Loss': win_loss,
    'KP Net Rtg': netrtg
})

kenpom_df.to_csv('kenpom.csv', index=False)