#! python3
# main.py - main script of the app.

import os

import pandas as pd

# Bokeh imports
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs

from data_scraping.scripts.data_funcs import get_gw_match_result, get_opponent
from scripts.basic_team_stats import basic_teams_stats_tab
from scripts.attacks_origin import attacks_origin_tab
from scripts.players_performances import players_performance_tab

# Import data and create dataFrames
data_dir = os.path.join(os.path.dirname(__file__),
                        os.path.join('data_scraping', 'data'))
team_stats_df = pd.read_csv(os.path.join(data_dir, 'teams_stats_by_gw.csv'))
players_stats_df = pd.read_csv(os.path.join(data_dir,
                                            'players_stats_by_gw.csv'))
players_info_df = pd.read_csv(os.path.join(data_dir, 'players_info.csv'))
results_df = pd.read_csv(os.path.join(data_dir, 'matches_results.csv'))

team_stats_df['Match result'] = team_stats_df.apply(get_gw_match_result,
                                                    args=[results_df], axis=1)
team_stats_df['Opponent'] = team_stats_df.apply(get_opponent,
                                                args=[results_df], axis=1)


# Creates tabs
tab1 = basic_teams_stats_tab(team_stats_df)
tab2 = attacks_origin_tab(team_stats_df)
tab3 = players_performance_tab(players_info_df, players_stats_df, results_df)

tabs = Tabs(tabs=[tab1, tab2, tab3])

curdoc().add_root(tabs)
