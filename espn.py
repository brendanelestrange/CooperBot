import time
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

# Define the URL
espn_url = "https://www.espn.com/mens-college-basketball/bpi"
driver.get(espn_url)

# Attempt to click "Load More" button until all teams are loaded
while True:
    try:
        # Find the "Show More" button using its class
        show_more_button = driver.find_element(By.CLASS_NAME, "loadMore__link")
        show_more_button.click()
        time.sleep(2)  # Wait for more content to load
    except NoSuchElementException:
        # If "Show More" button is not found, we assume all content is loaded
        break

# Parse the fully loaded page with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()  # Close the browser

# Initialize lists for team names and BPI data
team_names = []
bpi_data = []

# Loop through all rows to capture all teams and data
for row in soup.find_all('tr'):
    cols = row.find_all('td')
    if len(cols) == 2:  # Rows with team names
        team_full_name = cols[0].text.strip()
        team_names.append(team_full_name)
    elif len(cols) >= 7:  # Rows with BPI data          # Win-Loss record
        bpi_rating = cols[1].text.strip()      # BPI Rating
        bpi_rank = cols[2].text.strip()        # BPI Rank
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
espn_df.to_csv('espn.csv', index=False)