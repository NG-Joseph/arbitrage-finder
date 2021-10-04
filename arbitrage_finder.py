import pickle
from fuzzywuzzy import process, fuzz
from sympy import symbols, Eq, solve
import pandas as pd
from bookies.sportybet import sporty_df
from bookies.bet9ja import bet9ja_df

sporty_teams = sporty_df['Match'].tolist()
b9ja_teams = bet9ja_df['Match'].tolist()
sporty_df[['Bet9ja_Matches_Matched', 'Score_b9ja']] = sporty_df['Match'].apply(
    lambda x: process.extractOne(x, b9ja_teams, scorer=fuzz.token_set_ratio)).apply(pd.Series)
surebet_sporty_bet9ja = pd.merge(sporty_df, bet9ja_df, left_on='Bet9ja_Matches_Matched', right_on='Match')
surebet_sporty_bet9ja = surebet_sporty_bet9ja[surebet_sporty_bet9ja['Score_b9ja'] > 80]
surebet_sporty_bet9ja = surebet_sporty_bet9ja[
    ['Match_x', 'home_odds_x', 'away_odds_x', 'Match_y', 'home_odds_y', 'away_odds_y']]


def find_surebet(frame):
    frame['home_odds_x'] = frame['home_odds_x'].apply(pd.Series).astype(float)
    frame['away_odds_x'] = frame['away_odds_x'].apply(pd.Series).astype(float)
    frame['home_odds_y'] = frame['home_odds_y'].apply(pd.Series).astype(float)
    frame['away_odds_y'] = frame['away_odds_y'].apply(pd.Series).astype(float)

    frame['sure_btts1'] = (1/ frame['home_odds_x']) + (1 / frame['away_odds_y'])
    frame['sure_btts2'] = (1 / frame['away_odds_x']) + (1 / frame['home_odds_y'])
    frame = frame[
        ['Match_x', 'home_odds_x', 'away_odds_x', 'Match_y', 'home_odds_y', 'away_odds_y', 'sure_btts1', 'sure_btts2']]
    frame = frame[(frame['sure_btts1'] < 1) | (frame['sure_btts2'] < 1)]
    frame.reset_index(drop=True, inplace=True)
    return frame


surebet_sporty_bet9ja = find_surebet(surebet_sporty_bet9ja)
dict_surebet = {'sporty-bet9ja': surebet_sporty_bet9ja}


def beat_bookies(odds1, odds2, total_stake):
    x, y = symbols('x y')
    eq1 = Eq(x + y - total_stake, 0)  # total_stake = x + y
    eq2 = Eq((odds2 * y) - odds1 * x, 0)  # odds1*x = odds2*y
    stakes = solve((eq1, eq2), (x, y))
    total_investment = stakes[x] + stakes[y]
    profit1 = odds1 * stakes[x] - total_stake
    profit2 = odds2 * stakes[y] - total_stake
    benefit1 = f'{profit1 / total_investment * 100:.2f}%'
    benefit2 = f'{profit2 / total_investment * 100:.2f}%'
    dict_gambling = {'GG_Odds1': odds1, 'NG_Odds2': odds2, 'GG_Stake': f'${stakes[x]:.0f}',
                     'NG_Stake': f'{stakes[y]:.0f}%', 'Profit1': f'{profit1:.2f}%', 'Profit2': f'${profit2:.2f}',
                     'Benefit1': benefit1, 'Benefit2': benefit2}
    return dict_gambling


total_stake = 100  # set your total stake
for frame in dict_surebet:
    if len(dict_surebet[frame]) >= 1:
        print(
            '------------------SUREBETS Found! ' + frame + ' (check team names)--------------------------------------------------')
        print(dict_surebet[frame])
        print('------------------Stakes-------------------------')
        for i, value in enumerate(dict_surebet[frame]['sure_btts1']):
            if value < 1:
                odds1 = float(dict_surebet[frame].at[i, 'home_odds_x'])
                odds2 = float(dict_surebet[frame].at[i, 'away_odds_y'])
                teams = dict_surebet[frame].at[i, 'Match_x'].split(' vs ')
                dict_1 = beat_bookies(odds1, odds2, total_stake)
                print(str(i) + ' ' + '-'.join(teams) + '(sporty->bet9ja) ----> ' + ' '.join(
                    '{}:{}'.format(x, y) for x, y in dict_1.items()))
        for i, value in enumerate(dict_surebet[frame]['sure_btts2']):
            if value < 1:
                odds1 = float(dict_surebet[frame].at[i, 'away_odds_x'])
                odds2 = float(dict_surebet[frame].at[i, 'home_odds_y'])
                teams = dict_surebet[frame].at[i, 'Match_y'].split(' vs ')
                dict_1 = beat_bookies(odds1, odds2, total_stake)
                print(str(i) + ' ' + '-'.join(teams) + '(bet9ja->sporty) ----> ' + ' '.join(
                    '{}:{}'.format(x, y) for x, y in dict_1.items()))

    else:
        print("No surebets found! Try again later.")