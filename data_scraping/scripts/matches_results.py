#! python 3
# matches_results.py - Scrape data from IPL website.
# Verify that browsers' drivers are located in the same directory.

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from datetime import datetime

results_url = 'https://www.football.co.il/en/scores'


def initiate_driver():
    """Creates and returns a webdriver opened on relevant url."""

    driver = webdriver.Chrome()
    driver.get(results_url)
    return driver


def get_winner(score, teams):
    """

    :param score: list of 2 numbers.
    :param teams: list of 2 team's str.
    """
    if score[0] > score[1]:
        return teams[0]
    elif score[1] > score[0]:
        return teams[1]
    else:
        return 'Draw'


def get_results(driver):
    """Gets webdriver opened on 'results' page, returns matches results.

    :returns DataFrame.
    """
    html = driver.page_source
    soup = BeautifulSoup(html, features='lxml')
    gameweeks_elems = soup.select(
        'body > div.scores-page > div > '
        'div[class*="col-xs-12 games-round-container league-902"]')
    rows = []
    season = '19/20'  # currently const. Not available for other seasons.

    for gw_elem in gameweeks_elems:
        matches_elems = gw_elem.select(
            'div.current-round-details-view.col-xs-12 > '
            'div[class*="current-round-details-row"]')
        for match_elem in matches_elems:
            row = dict()
            row['Season'] = season
            row['Gameweek'] = int(match_elem['class'][6].split('-')[2])
            match_info = match_elem.find_all('label')
            row['Date'] = datetime.strptime(match_info[0].text, '%d.%m.%y')
            row['Day'] = match_info[1].text
            row['Game time'] = match_info[2].text
            teams = match_info[3].text.split(' - ')
            row['Home team'] = teams[0]
            row['Away team'] = teams[1]
            score = match_info[4].text.strip().split(' - ')
            if len(score) < 2:
                continue
            row['Home team score'] = int(score[0])
            row['Away team score'] = int(score[1])
            row['Winner'] = get_winner(score, teams)
            row['Stadium'] = match_info[5].text
            rows.append(row)

    # results_df = pd.DataFrame(data=rows, columns=rows[0].keys())

    return rows  # results_df


if __name__ == '__main__':
    driver = initiate_driver()
    # df = get_results(driver)
    driver.close()
    # df.to_csv('matches_results.csv', index=False)
