import time
import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

# Set up Selenium WebDriver with webdriver_manager
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Optional: Run in headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

espn_url = "https://www.espn.com/mens-college-basketball/bpi"
driver.get(espn_url)


while True:
    try:
        
        show_more_button = driver.find_element(By.CLASS_NAME, "loadMore__link")
        show_more_button.click()
        time.sleep(2)  
    except NoSuchElementException:
    
        break


soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()  


team_names = []
bpi_data = []


for row in soup.find_all('tr'):
    cols = row.find_all('td')
    if len(cols) == 2:  
        team_full_name = cols[0].text.strip()
        team_names.append(team_full_name)
    elif len(cols) >= 7:  
        bpi_rating = cols[1].text.strip()      
        bpi_rank = cols[2].text.strip()        
        bpi_data.append([bpi_rating, bpi_rank])

# Check and verify data length
print(f"Total teams captured: {len(team_names)}")
print(f"Total BPI data entries captured: {len(bpi_data)}")

# Combine team names with BPI data
if len(team_names) == len(bpi_data):
    espn_data = [
        [f"{team_names[i]}"] + bpi_data[i][:] for i in range(len(team_names))
    ]
    espn_df = pd.DataFrame(espn_data, columns=["Team", "BPI Rating", "BPI Rank"])
    print(espn_df)
else:
    print("Mismatch in data length between team names and BPI data lists.")
    print(f"Team names found: {len(team_names)}")
    print(f"BPI data entries found: {len(bpi_data)}")
    
    #Ensure the "results" folder exists
os.makedirs("results", exist_ok=True)

espn_df.to_csv('results/espn.csv', index=False)