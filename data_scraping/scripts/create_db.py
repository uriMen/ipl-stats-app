#! python 3
# create_db.py - create database with sqlite.

import sqlite3
from sqlite3 import Error, OperationalError
import os

from data_scraping.scripts import matches_results, stats, players_info


def create_connection(db_file_path):
    """Create a connection to sqlite db.

    :return: sqlite Connection object or None.
    """

    conn = None
    try:
        conn = sqlite3.connect(db_file_path)
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql_query):
    """

    :param conn: sqlite connection to db object.
    :param create_table_sql_query: str. Sql query.
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql_query)
    except Error as e:
        print(e)


def add_col_to_table(conn, table_name, col, col_type):
    """Add column to a table in database.

    :param conn: connection object.
    :param table_name: str.
    :param col: str. Column name.
    :param col_type: str. Type of column data.
    """
    c = conn.cursor()
    try:
        with conn:
            c.execute(f"""ALTER TABLE {table_name} 
                          ADD COLUMN {col} {col_type}""")
    except OperationalError:
        return


def clear_table(conn, table_name):
    """Delete all rows in table."""
    c = conn.cursor()
    with conn:
        c.execute(f"""DELETE FROM {table_name}""")


def create_results_table(conn):
    """Create matches results table

    :param conn: Connection to db object.
    """
    driver = matches_results.initiate_driver()
    c = conn.cursor
    create_table_query = """CREATE TABLE IF NOT EXISTS matches_results (
                                season text,
                                gameweek integer,
                                date text,
                                day text,
                                game_time text,
                                home_team text,
                                away_team text,
                                home_score integer,
                                away_score integer,
                                winner text,
                                stadium text
                                )"""
    create_table(conn, create_table_query)
    # clear table so we can use this function
    # as 'update' function as well - just re-collect
    # all matches results.
    clear_table(conn, 'matches_results')
    # insert matches results data
    results = matches_results.get_results(driver)
    for r in results:
        insert_result(conn, r)


def insert_result(conn, result):
    """Insert match result data to table.

    :param conn: connection object to sqlite db.
    :param result: dict. Match data.
    """
    c = conn.cursor()
    with conn:
        c.execute("""INSERT INTO matches_results VALUES (
                        :season,
                        :gameweek,
                        :date,
                        :day,
                        :game_time,
                        :home_team,
                        :away_team,
                        :home_score,
                        :away_score,
                        :winner,
                        :stadium
                        )""",
                  {'season': result['Season'], 'gameweek': result['Gameweek'],
                   'date': result['Date'], 'day': result['Day'],
                   'game_time': result['Game time'],
                   'home_team': result['Home team'],
                   'away_team': result['Away team'],
                   'home_score': result['Home team score'],
                   'away_score': result['Away team score'],
                   'winner': result['Winner'], 'stadium': result['Stadium']})


def modify_column_name(col_name):
    """replace whitespaces with underscores."""
    return col_name.lower().replace(' ', '_')


def create_stats_tables(conn):
    """Create stats tables in sqlite database."""

    # create table in db
    create_players_stats_query = """CREATE TABLE IF NOT EXISTS 
                                        players_stats_by_gw (
                                            pid integer,
                                            season text,
                                            gameweek integer
                                            )"""
    create_teams_stats_query = """CREATE TABLE IF NOT EXISTS 
                                        teams_stats_by_gw (
                                            team text,
                                            season text,
                                            gameweek integer
                                            )"""
    create_table(conn, create_players_stats_query)
    create_table(conn, create_teams_stats_query)

    # collect data.
    driver = stats.initiate_driver()
    # players data.
    p_data = stats.stats_per_game_wrapper(driver, 'player')
    # Initiate drive
    driver.close()
    driver = stats.initiate_driver()
    # teams data
    t_data = stats.stats_per_game_wrapper(driver, 'team')

    # Populate tables with data.
    insert_data_to_stats_tables(conn, p_data, 'player')
    insert_data_to_stats_tables(conn, t_data, 'team')


def insert_data_to_stats_tables(conn, data, item_type):
    """Insert stats to tables in database.

    :param conn: db connection object.
    :param data: list of tuples in the form of
    (data (dict), season (str), gameweek (str))
    :param item_type: str. One of ['player', 'team']
    """
    c = conn.cursor()
    table_name = {'player': 'players_stats_by_gw',
                  'team': 'teams_stats_by_gw'}
    id_col = {'player': 'pid', 'team': 'team'}
    for data_tup in data:
        for att, values in data_tup[0].items():
            att = modify_column_name(att)
            add_col_to_table(conn, table_name[item_type], att,
                             'real DEFAULT 0')
            with conn:
                for item_id, stat in values.items():
                    # check if pid/team already in table.
                    # If so, update its value in new col
                    # els, insert a new row
                    pid_row = c.execute(
                        f"""SELECT * FROM {table_name[item_type]} 
                              WHERE {id_col[item_type]} = :id 
                              AND season = :season 
                              AND gameweek = :gw""",
                        {'id': item_id, 'season': data_tup[1],
                         'gw': data_tup[2]}
                    ).fetchone()
                    if pid_row:
                        c.execute(
                            f"""UPDATE {table_name[item_type]} 
                                SET {att} = :value 
                                WHERE {id_col[item_type]} = :id 
                                AND season = :season 
                                AND gameweek = :gw""",
                            {'value': stat, 'id': item_id,
                             'season': data_tup[1], 'gw': data_tup[2]})
                    else:
                        c.execute(
                            f"""INSERT INTO {table_name[item_type]} (
                                    {id_col[item_type]}, 
                                    season, 
                                    gameweek,
                                    {att}) 
                                VALUES (:id, :season, :gw, :value)""",
                            {'id': item_id, 'season': data_tup[1],
                             'gw': data_tup[2], 'value': stat})


def create_players_info_table(conn):
    """Create players info table in db and insert data."""
    c = conn.cursor()
    driver = stats.initiate_driver()
    create_table_query = """CREATE TABLE IF NOT EXISTS players_info (
                                pid integer PRIMARY KEY,
                                name text,
                                shirt_number integer,
                                team text,
                                position text,
                                date_of_birth text
                                )"""
    insert_player_query = """INSERT INTO players_info VALUES (
                                :pid, :name, :shirt, :team, :pos, :dob
                                )"""
    create_table(conn, create_table_query)

    get_pids_query = """SELECT DISTINCT pid FROM players_stats_by_gw"""
    pids = [tup[0] for tup in c.execute(get_pids_query).fetchall()]
    for pid in pids:
        # check if player exists in table
        if not c.execute("""SELECT * FROM players_info WHERE pid = :id""",
                         {'id': pid}).fetchall():
            # get player info
            p_info = players_info.get_player_info(driver, pid)
            if p_info:
                with conn:
                    c.execute(insert_player_query,
                              {'pid': p_info['pid'],
                               'name': p_info['Name'],
                               'shirt': p_info['Shirt number'],
                               'team': p_info['Team'],
                               'pos': p_info['Position'],
                               'dob': p_info['Date of birth']})


def clean_data(conn):
    """ Delete some rows from tables."""
    c = conn.cursor()
    with conn:
        # delete rows of players from teams not in the league
        c.execute("""DELETE FROM players_info WHERE team NOT IN (
                         SElECT DISTINCT team from teams_stats_by_gw
                         )""")


def main():
    # connect to sqlite database
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    db_file_path = os.path.join(data_dir, 'ipl_data.db')

    conn = create_connection(db_file_path)

    # create and populate tables in db.
    create_stats_tables(conn)
    create_players_info_table(conn)
    create_results_table(conn)

    clean_data(conn)

    conn.close()


if __name__ == '__main__':
    main()
