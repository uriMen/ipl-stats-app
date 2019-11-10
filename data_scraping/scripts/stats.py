#! python 3
# stats.py - Scrape data from IPL website.
# Verify that browsers' drivers are located in the same directory.

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common import exceptions
from selenium.webdriver.common.keys import Keys
# from datetime import datetime

# import time

base_url = 'https://www.football.co.il'
stats_url = 'https://www.football.co.il/en/stats'


def initiate_driver():
    """Creates and returns a webdriver opened on relevant url."""

    driver = webdriver.Chrome()
    driver.get(stats_url)
    return driver


def unfold_stats(driver):
    """click 'Show More' to reveal all hidden stats."""

    while True:
        try:
            WebDriverWait(driver, 5).until(ec.presence_of_element_located(
                ('class name', 'stats-see-more-btn')))
            driver.find_element_by_class_name('stats-see-more-btn').click()
        except exceptions.TimeoutException:
            return


def unfold_players(driver):
    """click 'Full List' buttons to reveal all hidden players."""

    try:
        WebDriverWait(driver, 5).until(ec.presence_of_element_located(
            ('class name', 'stats-category-full-list-label')))
        btns = driver.find_elements_by_class_name(
            'stats-category-full-list-label')
        for btn in btns:
            btn.click()
    except exceptions.TimeoutException:
        return


def select_item_type(driver, item_type):
    """

    :param driver: webdriver object
    :param item_type: str. 'player' or 'team'
    :return:
    """
    driver.find_element_by_xpath(
        '//*[@id="stats-page-widget-react"]/div/ul/li[1]/span').click()
    type_selector = driver.find_element_by_xpath(
        '/html/body/span/span/span[1]/input')
    type_selector.send_keys(item_type)
    type_selector.send_keys(Keys.ENTER)


def select_season(driver, season):
    """Filter stats on web page by season."""

    driver.find_element_by_xpath(
        '//*[@id="stats-page-widget-react"]/div/ul/li[7]/span/span[1]'
        '/span').click()
    season_selector = driver.find_element_by_xpath(
        '/html/body/span/span/span[1]/input')
    season_selector.send_keys(season)
    season_selector.send_keys(Keys.ENTER)


def select_gameweek(driver, gw):
    """Filter stats on web page by game week."""

    driver.find_element_by_xpath(
        '//*[@id="stats-page-widget-react"]/div/ul/li[4]/span').click()
    gw_selector = driver.find_element_by_xpath(
        '/html/body/span/span/span[1]/input')
    gw_selector.send_keys(gw)
    gw_selector.send_keys(Keys.ENTER)


def select_position(driver, pos='all'):
    """Filter stats on web page by position."""

    if pos == 'all':
        driver.find_element_by_xpath('//*[@id="select2-selectPosition'
                                     '-container"]/span').click()
        driver.find_element_by_xpath(
            '//*[@id="stats-page-widget-react"]/div/ul/li[2]/span/span[1]'
            '/span').click()
    else:
        driver.find_element_by_xpath(
            '//*[@id="stats-page-widget-react"]/div/ul/li[2]/span/span[1]'
            '/span').click()
        gw_selector = driver.find_element_by_xpath(
            '/html/body/span/span/span[1]/input')
        gw_selector.send_keys(pos)
        gw_selector.send_keys(Keys.ENTER)


def get_soup(driver):
    """Returns a BeautifulSoup object of current web page."""

    html = driver.page_source
    driver.close()
    return BeautifulSoup(html)


def get_stat_label(elem):
    """Gets web element of stat table, returns its label"""

    label = elem.find_all('div', recursive=False)[0].contents[1].text
    return label


def get_player_id_score(player):
    """Gets player element from stat table, returns id and score"""

    p_id = int(player.contents[0]['href'].split('player/')[1])
    p_score = int(player.contents[2].text)
    return p_id, p_score


def get_team_score(team):
    """Gets team element from stat table, returns team name and score"""

    t_name = team.contents[1].text
    t_score = float(team.contents[2].text)
    return t_name, t_score


def stats_scraper(stats, item_type='player'):
    """Gets a list of web elements, returns players stats.

    :param stats: List of web elements of stats tables
    :param item_type: str. Available inputs: 'player' or 'team'.
    Default: 'players'.
    :returns nested dict of the form {stat: {player_id: score}}
    """

    items_stats = dict()
    for stat in stats:
        label = get_stat_label(stat)
        if (label not in items_stats) and (label not in ['SubIn', 'SubOut']):
            items_score = dict()
            items = stat.find_all('li')
            for item in items:
                if item_type == 'player':
                    item_id, score = get_player_id_score(item)
                    items_score[item_id] = score
                elif item_type == 'team':
                    item_id, score = get_team_score(item)
                    items_score[item_id] = score
            items_stats[label] = items_score

    return items_stats


def create_stats_df(items_stats, season, gw, item_type='player'):
    """

    :param items_stats: dict. Returned object from stats_scraper().
    :param season: str. Desired season
    :param gw: str. Desired gameweek
    :param item_type: str. Available inputs: 'player' or 'team'.
    Default: 'player'.
    :return: DataFrame with players stats from given season and gw.
    """
    rows_for_df = []
    if item_type == 'player':
        for item_id in items_stats['Minutes'].keys():
            row = dict()
            row['pid'] = item_id
            for att, values in items_stats.items():
                if item_id in values:
                    row[att] = values[item_id]
                else:
                    row[att] = 0
            rows_for_df.append(row)

    elif item_type == 'team':
        for item_id in items_stats['Ball Possession'].keys():
            row = dict()
            row['Team'] = item_id
            for att, values in items_stats.items():
                if item_id in values:
                    row[att] = values[item_id]
                else:
                    row[att] = 0
            rows_for_df.append(row)

    id_col_name = {'player': 'pid', 'team': 'Team'}
    df = pd.DataFrame(data=rows_for_df,
                      columns=[id_col_name[item_type]]
                              + list(items_stats.keys()))

    df['Season'] = season
    df['Gameweek'] = gw
    return df


def stats_per_game_wrapper(driver, item_type='player'):
    """Collects stats and returns them in a Dataframe.

    :param driver: Webdriver object. Opened on 'stats' url.
    :param item_type: str. can one of ['player', 'team']
    :returns a Dataframe with per match stats.
    """

    seasons = ['19/20']
    gws = range(1, 9)
    df = pd.DataFrame()
    select_item_type(driver, item_type)

    # unfold hidden items on web page
    unfold_stats(driver)
    unfold_players(driver)

    for season in seasons:
        select_season(driver, season)
        for gw in gws:
            select_gameweek(driver, gw)
            soup = BeautifulSoup(driver.page_source, features='lxml')
            poi = soup.select('#stats-page-widget-react > div > div',
                              recursive=False)
            if item_type == 'player':
                # get gk stats
                select_position(driver, 'goalie')
                unfold_players(driver)
                soup = BeautifulSoup(driver.page_source, features='lxml')
                poi = poi + soup.select('#stats-page-widget-react > div > div',
                                        recursive=False)
                # reset position selection
                select_position(driver, 'all')

            scraped_stats = stats_scraper(poi, item_type)
            temp_df = create_stats_df(scraped_stats, season, gw, item_type)
            df = df.append(temp_df, ignore_index=True, sort=False)

    return df


if __name__ == '__main__':

    driver = initiate_driver()
    # p_df = stats_per_game_wrapper(driver, 'player')
    p_df = pd.read_csv('players_stats_by_gw.csv')

    pids = p_df['pid'].unique()
    # info_df = create_players_info_df(driver, pids)
    # info_df.to_csv('players_info.csv', index=False)
    # p_df.to_csv('players_stats_by_gw.csv', index=False)
    # t_df = stats_per_game_wrapper(driver, 'team')
    # t_df.to_csv('teams_stats_by_gw.csv', index=False)
    driver.close()
