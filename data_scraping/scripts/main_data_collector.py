#! python 3
# main_data_collector.py - Scrape data from IPL website.
# Verify that browsers' drivers are located in the same directory.

import os

from data_scraping.scripts import stats, matches_results, players_info, \
    create_db

data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

driver = stats.initiate_driver()

# Collect data
# Get teams stats
t_df = stats.stats_per_game_wrapper(driver, 'team')

# Get players stats
p_df = stats.stats_per_game_wrapper(driver, 'player')

# Get Players info
# try update csv if already exists
pids = p_df['pid'].unique()
p_info_df = players_info.update_player_info_df(driver, pids)
if p_info_df.empty:
    p_info_df = players_info.create_players_info_df(driver, pids)

# Get matches results
driver.get(matches_results.results_url)
results_df = matches_results.get_results(driver)

# Clean data
results_df.dropna(inplace=True)
pl_teams = sorted(t_df['Team'].unique())
# remove rows of players from teams not in the above list.
# get ids
ids_to_remove = []
idx_to_remove_from_info_df = []
for i, player in p_info_df.iterrows():
    if player['Team'] not in pl_teams:
        ids_to_remove.append(player['pid'])
        idx_to_remove_from_info_df.append(i)

idx_to_remove_from_stats_df = p_df[p_df['pid'].isin(ids_to_remove)].index
p_info_df.drop(index=idx_to_remove_from_info_df, inplace=True)
p_df.drop(index=idx_to_remove_from_stats_df, inplace=True)

p_df.reset_index(inplace=True)
p_info_df.reset_index(inplace=True)

# Save DataFrames to csv files
p_df.to_csv(f'{data_dir}\\players_stats_by_gw.csv', index=False)
t_df.to_csv(f'{data_dir}\\teams_stats_by_gw.csv', index=False)
p_info_df.to_csv(f'{data_dir}\\players_info.csv', index=False)
results_df.to_csv(f'{data_dir}\\matches_results.csv', index=False)

driver.close()
