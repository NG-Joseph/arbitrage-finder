"""
DISCLAIMER: This project is heavily inspired by DataDrivenInvestor's medium article on scraping from betting websites to find
surebets. Find this article at: https://medium.datadriveninvestor.com/make-money-with-python-the-sports-arbitrage-project-3b09d81a0098
"""
from re import search
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd

# changing chromedriver default options
options = Options()
options.headless = True
options.add_argument('window-size=1920x1080')  # Headless = True

web = 'https://sports.bet9ja.com/sport/soccer/1'
path = '/Users/jcool/chromedriver_win32/chromedriver.exe'  # introduce your file's path inside '...'

# execute chromedriver with edited options
driver = webdriver.Chrome(path, options=options)
driver.get(web)

teams = []
x12 = []  # wins,draws, losses
btts = []
over_under = []
odds_events = []
market_tabs = []  # dropdowns
matches_dicts = []

for entry in driver.get_log('browser'):
    print(entry)
# the top level bar that contains Highlights and Upcoming
matches_section = WebDriverWait(driver, 5).until \
    (EC.presence_of_all_elements_located((By.CLASS_NAME, 'sports-view__nav')))
for item in matches_section:
    matches_group_tabs = item.find_elements_by_class_name('sports-view__nav-tab-item')
    matches_group_tabs[1].click()
    print(f'Switched {matches_group_tabs[1].text} tab successfully')
    print("Next: Click on GG/NG tab")

markets_section = WebDriverWait(driver, 5).until \
        (EC.presence_of_all_elements_located(
        (By.XPATH, '//*[@id="wrapper"]/main/div/div/div/div[2]/div/div/div[1]/div[3]')))
height = driver.execute_script("return document.body.scrollHeight")
for item in markets_section:
    btts_tab = item.find_element_by_xpath("//td[@title='GG/NG']")
    btts_tab.click()
    print(f'Clicked on {btts_tab.text} tab successfully')

for i in range(height):
    driver.execute_script(f'window.scrollBy(0,20)')
    height = driver.execute_script("return document.body.scrollHeight")

matches_container = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'sports-table')))
for item in matches_container:
    match_rows = item.find_elements_by_class_name('table-f')

print("scrapping odds...")
height = driver.execute_script("return document.body.scrollHeight")

for match_row in match_rows:

    try:

        home_team = match_row.find_element_by_class_name('sports-table__home').text
        away_team = match_row.find_element_by_class_name('sports-table__away').text
        odds = match_row.find_elements_by_class_name('sports-table__odds-item')
        # accomodate possibility of empty odds...
        if odds[0].text == '':
            home_odds = 0.0
            away_odds = 0.0
        else:
            # below are ternary operators to catch empty odds
            home_odds = float(odds[0].text) if type(float(odds[0].text)) == float else 'N/A'
            away_odds = float(odds[1].text) if type(float(odds[1].text)) == float else 'N/A'
        matches_dicts.append(
            {'id': match_rows.index(match_row) + 1, 'Match': f'{home_team} vs {away_team}', 'game_type': 'gg/ng',
             'home_odds': home_odds, 'away_odds': away_odds})

    except Exception as e:
        print(f'Error was at item {match_rows.index(match_row) + 1}: {e}')  # index + 1 = Id

print("Done! Successful")

for item in matches_dicts:

    if bool(search("Srl", item["Match"])):
        new_match = item["Match"].split(" vs ")
        for team in new_match:
            new_match[new_match.index(team)] += " (Simulated League)"

        item["Match"] = " vs ".join(new_match)

    elif bool(search("Women", item["Match"])):
        new_match = item["Match"].split(" vs ")
        for team in new_match:
            new_match[new_match.index(team)] += " (Women)"

        item["Match"] = " vs ".join(new_match)

    elif bool(search("U19", item["Match"])):
        new_match = item["Match"].split(" vs ")
        for team in new_match:
            new_match[new_match.index(team)] += ""
        item["Match"] = " vs ".join(new_match)

    else:
        new_match = item["Match"].split(" vs ")
        for team in new_match:
            new_match[new_match.index(team)] += " (Main)"

        item["Match"] = " vs ".join(new_match)

bet9ja_df = pd.DataFrame(matches_dicts)
# bet9ja_df = bet9ja_df[bet9ja_df["Match"].str.contains('Srl')]






























