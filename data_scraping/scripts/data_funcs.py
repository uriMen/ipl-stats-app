#! python 3
# data_funcs.py - sunctions for data manipulating.


def get_gw_match_result(row, results_df):
    """Gets a row from team_stats df, returns 'w','d' or 'l'.

    :param row: pd.Series. A row of player/team stats DataFrame.
    :param results_df: results_df: pd.DataFrame. Matches results table.
    """
    match_row = results_df[(results_df.isin([row['Team']]).any(axis=1)) &
                           (results_df['Gameweek'] == row['Gameweek'])]

    result = match_row.iloc[0]['Winner']
    if result == row['Team']:
        return 'w'
    elif result == 'Draw':
        return 'd'
    else:
        return 'l'


def get_opponent(row, results_df):
    """Gets a row from player/team stats df, returns opponent in match.

    :param row: pd.Series. A row of player/team stats DataFrame.
    :param results_df: pd.DataFrame. Matches results table.
    """
    match_row = results_df[(results_df.isin([row['Team']]).any(axis=1)) &
                           (results_df['Gameweek'] == row['Gameweek'])].iloc[0]

    if match_row['Home team'] == row['Team']:
        return match_row['Away team']
    else:
        return match_row['Home team']
