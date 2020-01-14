#! python 3
# players_info.py - Scrape data from IPL website.
# Verify that browsers' drivers are located in the same directory.

import os

from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


def get_player_info(driver, player_id):
    """Scrape player info from his own url. Returns dict."""
    # Rename positions
    positions = {'defenseman': 'Defender', 'mid-fielder': 'Midfielder',
                 'goalie': 'GK', 'forward': 'Forward'}

    try:
        driver.get(f'https://www.football.co.il/en/player/{player_id}')
        player_html = driver.page_source
        player_soup = BeautifulSoup(player_html, features='lxml')
        p_info = player_soup.select('body > div.player-page > div >'
                                    'div.col-md-8.col-xs-12.player-right-side '
                                    '> div.player-details.col-xs-12')[0].text

        name_number = \
            player_soup.select('.player-page > div > div > div > div',
                               recursive=False)[0].text
        p_row = dict()
        p_row['pid'] = player_id
        p_row['Name'] = name_number.split(' | ')[0]
        p_row['Shirt number'] = name_number.split(' | ')[1]
        p_row['Team'] = p_info.split(' | ')[0].split('Team: ')[1]
        position = p_info.split(' | ')[1].split('Position: ')[1]
        p_row['Position'] = positions[position]
        dob = p_info.split(' | ')[2].split('Date of birth: ')[1]
        p_row['Date of birth'] = datetime.strptime(dob, '%d.%m.%y')
        return p_row

    except IndexError:
        print(f'error: player id: {player_id}')
        return None


def create_players_info_df(driver, p_ids):
    """Gets a list of players ids, returns a Dataframe with info"""

    rows = []
    for pid in p_ids:
        row = get_player_info(driver, pid)
        if row:
            rows.append(row)
    p_info_df = pd.DataFrame(data=rows)
    # Rename positions
    # positions = {'defenseman': 'Defender', 'mid-fielder': 'Midfielder',
    #              'goalie': 'GK', 'forward': 'Forward'}
    # p_info_df.replace(positions, inplace=True)

    return p_info_df


def update_player_info_df(driver, p_ids):
    """Gets a list of players ids, adds new rows if needed."""

    try:
        temp_df = pd.read_csv(os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data', 'players_info.csv'))

    except FileNotFoundError:
        return pd.DataFrame()   # empty Dataframe.

    cur_pids = temp_df['pid'].unique()
    p_ids_to_add = list(set(p_ids) - set(cur_pids))

    rows_to_add = []
    for pid in p_ids_to_add:
        rows_to_add.append(get_player_info(driver, pid))

    temp_df = temp_df.append(rows_to_add, ignore_index=True)

    return temp_df

