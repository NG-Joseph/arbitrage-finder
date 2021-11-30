
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# changing chromedriver default options
options = Options()
options.headless = True
options.add_argument('window-size=1920x1080')  # Headless = True

web = 'https://www.sportybet.com/ng/sport/football/today'
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
market_tabs2 = []  # dropdowns
matches_dicts = []

"""TODO: Add functionality for switching pages when there are more games"""
try:
    pagination_switch_container = WebDriverWait(driver, 4).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'pagination')))

except Exception as e:
    print(e)
    pagination_switch_container = []  # Set pagination
    print('Only one page exists')

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

match_rows = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'match-row')))
count = 0
for match_row in match_rows:
    count += 1
    home_team = match_row.find_element_by_class_name('home-team').text
    away_team = match_row.find_element_by_class_name('away-team').text
    parent = match_row.find_element_by_xpath('./..')  # immediate parent node
    # update 4 (+3 times .find_element_by_xpath('./..'))
    grandparent = parent.find_element_by_xpath('./..')
    league_container = grandparent.find_element_by_class_name('league-title')
    league = league_container.find_element_by_class_name('text').text

    odds = match_row.find_elements_by_class_name('m-outcome-odds')
    try:
        home_odds = float(odds[0].text)  # home comes first
        away_odds = float(odds[1].text)  # away comes second
    except Exception as e:
        print(f'{home_team} vs {away_team}')
        print('error was at', match_rows.index(match_row), e)

    matches_dicts.append(
        {'id': match_rows.index(match_row) + 1, 'Match': f'{home_team} vs {away_team}', 'game_type': 'gg/ng',
         'home_odds': home_odds, 'away_odds': away_odds, 'league': league})
print("scraped first page")
if len(pagination_switch_container) >= 1:  # pagination renders conditionally. Execute the below logic only if its found
    for pagination in pagination_switch_container:
        pagination_switch = pagination.find_elements_by_class_name("pageNum")
    print("pagination count:", len(pagination_switch))
    if len(
            pagination_switch) > 3:  # if only one page, 3 things have 'pageNum' class name, previous icon, current page (1) and next icon
        print('switching page...')
        pagination_switch[2].click()  # click on the number 2 button
        time.sleep(2)

        league_wraps2 = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'match-league')))

        for league_wrap in league_wraps2:
            # append all the market items (3way,double chance) to market_tabs array and click on it
            market_tabs2.append(league_wrap.find_elements_by_class_name("market-item"))
            market_tabs2[league_wraps2.index(league_wrap)][2].click()
            """for match in league_wrap:
                home_team = league_wrap[match].find_elements_by_class_name('home-team')
                away_team = league_wrap[match].find_elements_by_class_name('away-team')
                teams.append([home_team,away_team])"""

        match_rows2 = WebDriverWait(driver, 2).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'match-row')))

        for match_row in match_rows2:
            home_team = match_row.find_element_by_class_name('home-team').text
            away_team = match_row.find_element_by_class_name('away-team').text
            odds = match_row.find_elements_by_class_name('m-outcome-odds')
            parent = match_row.find_element_by_xpath('./..')  # immediate parent node
            # update 4 (+3 times .find_element_by_xpath('./..'))
            grandparent = parent.find_element_by_xpath('./..')
            league_container = grandparent.find_element_by_class_name('league-title')
            league = league_container.find_element_by_class_name('text').text
            try:
                home_odds = float(odds[0].text)  # home comes first
                away_odds = float(odds[1].text)  # away comes second

            except Exception as e:
                home_odds = 0.0  # home comes first
                away_odds = 0.0  # away comes second
                print(f'{home_team} vs {away_team}')
                print('error was at', match_rows2.index(match_row) + len(match_rows), e)
            matches_dicts.append(
                {'id': match_rows2.index(match_row) + len(match_rows) + 1, 'Match': f'{home_team} vs {away_team}',
                 'game_type': 'gg/ng', 'home_odds': home_odds, 'away_odds': away_odds, 'league': league})

    else:
        pass

# next step: get home and away odds as well as team names in a dict and append it into a new array
'''for i in matches_dicts:
    print(i)'''
'''If a league has SRL add a whole new extra string to make matching better'''
u19leagues = [
    "International Youth UEFA Youth League"
]

women_leagues = [
    "Spain Primera Division Women", "Finland Kansallinen Liiga, Women", "Scotland Premier League 1, Women",
    "England Amateur Fa Cup, Women"
]

simulated_leagues = ["Simulated Reality League UEFA Champions League SRL"]

# Add more context to Sporty team names to make string matching more accurate
for item in matches_dicts:
    if item["league"] in u19leagues:
        new_match = item["Match"].split(" vs ")
        for team in new_match:
            new_match[new_match.index(team)] += " U19"
        item["Match"] = " vs ".join(new_match)

    elif item["league"] in simulated_leagues:
        new_match = item["Match"].split(" vs ")
        for team in new_match:
            new_match[new_match.index(team)] += " (Simulated League)"
        item["Match"] = " vs ".join(new_match)

    elif item["league"] in women_leagues:
        new_match = item["Match"].split(" vs ")
        for team in new_match:
            new_match[new_match.index(team)] += " (Women)"
        item["Match"] = " vs ".join(new_match)

    else:
        new_match = item["Match"].split(" vs ")
        for team in new_match:
            new_match[new_match.index(team)] += " (Main)"
        item["Match"] = " vs ".join(new_match)

sporty_df = pd.DataFrame(matches_dicts)
# sporty_df = sporty_df[~sporty_df["Match"].str.contains('SRL')]
print('done')

















