"""
DISCLAIMER: This project is heavily inspired by DataDrivenInvestor's medium article on scraping from betting websites to find
surebets. Find this article at: https://medium.datadriveninvestor.com/make-money-with-python-the-sports-arbitrage-project-3b09d81a0098
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

#changing chromedriver default options
options = Options()
options.headless = True
options.add_argument('window-size=1920x1080') #Headless = True

web = 'https://www.sportybet.com/ng/sport/football/today'
path = '/Users/jcool/chromedriver_win32/chromedriver.exe' #introduce your file's path inside '...'

#execute chromedriver with edited options
driver = webdriver.Chrome(path, options=options)
driver.get(web)

teams = []
x12 = []  # wins,draws, losses
btts = []
over_under=[]
odds_events = []
market_tabs = [] # dropdowns
matches_dicts = []


for entry in driver.get_log('browser'):
    print(entry)

league_wraps = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'match-league')))

for league_wrap in league_wraps:

    # append all the market items (3way,double chance) to market_tabs array and click on it
    market_tabs.append(league_wrap.find_elements_by_class_name("market-item"))
    market_tabs[league_wraps.index(league_wrap)][2].click()
    """for match in league_wrap:
        home_team = league_wrap[match].find_elements_by_class_name('home-team')
        away_team = league_wrap[match].find_elements_by_class_name('away-team')
        teams.append([home_team,away_team])"""

match_rows = WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'match-row')))

for match_row in match_rows:
    home_team = match_row.find_element_by_class_name('home-team').text
    away_team = match_row.find_element_by_class_name('away-team').text
    odds = match_row.find_elements_by_class_name('m-outcome-odds')
    try:
        home_odds = float(odds[0].text) # home comes first
        away_odds = float(odds[1].text) # away comes second
    except:
        print('error was at', match_rows.index(match_row))


    matches_dicts.append({'home_team': home_team, 'away_team': away_team, 'home_odds': home_odds, 'away_odds': away_odds})




# next step: get home and away odds as well as team names in a dict and append it into a new array
for i in matches_dicts:
    print(i)





'''
win_lose_draw_tab = Select(market_tabs[0])
double_chance_tab = Select(market_tabs[1])
gg_or_ng_tab = Select(market_tabs[2])
draw_no_bet_tab = Select(market_tabs[3])
other_markets_tab = Select(market_tabs[4])
'''












