from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import pickle

options = Options()
options.headless = True
options.add_argument('window-size=1920x1080')

web = 'https://www.betfair.com/sport/inplay'
path = '/Users/jcool/chromedriver_win32/chromedriver.exe' #introduce your file's path inside '...'from selenium import webdriver


driver = webdriver.Chrome(path, options=options)
driver.get(web)
# driver.maximize_window()

#option1
# accept = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')))
#option 2
time.sleep(2)
accept = driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]')
accept.click()
dict_odds = {}

#choose any market you want
markets = ['Más/menos de 2,5 goles', '¿Marcarán ambos equipos?']

for i, market in enumerate(markets):
    dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'dropdown-1')))
    dropdown.click()

    list_odds = []
    teams = []
    time.sleep(1)
    box = driver.find_element_by_xpath('//div[contains(@data-sport-id,"1")]') #livebox -> diferent sports //  #upcoming = comingup
    rows = WebDriverWait(box, 5).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'com-coupon-line')))
    for row in rows:
        odds = row.find_element_by_xpath('.//div[contains(@class, "runner-list")]')
        list_odds.append(odds.text)
        home = row.find_element_by_class_name('home-team-name').text
        away = row.find_element_by_class_name('away-team-name').text
        teams.append(home + '\n' + away)
    dict_odds['odds_%s' % i] = list_odds
    dict_odds['teams_%s' % i] = teams

driver.quit()

# unlimited columns
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

df_1 = pd.DataFrame({'Teams':dict_odds['teams_0'], 'over2.5':dict_odds['odds_0']}).set_index('Teams')
df_btts = pd.DataFrame({'Teams':dict_odds['teams_1'], 'btts':dict_odds['odds_1']}).set_index('Teams')

df_betfair = pd.concat([df_1, df_btts], axis=1, sort=True)
df_betfair.reset_index(inplace=True)
df_betfair.rename(columns={'index':'Teams'}, inplace=True)

df_betfair = df_betfair.fillna('')
df_betfair = df_betfair.replace('SUSPENDIDO\n', '', regex=True)#Spanish
df_betfair = df_betfair.applymap(lambda x: x.strip() if isinstance(x, str) else x) #14.0\n

#save file
output = open('df_betfair', 'wb')
pickle.dump(df_betfair, output)
output.close()
print(df_betfair)