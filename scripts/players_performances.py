#! python 3
# players_performances.py - create tab for bokeh app
# with players performances data.

import pandas as pd
import numpy as np

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, Panel
from bokeh.models.widgets import Select, CheckboxButtonGroup
from bokeh.layouts import row, widgetbox
from bokeh.palettes import Category20_20

from data_scraping.scripts.data_funcs import get_opponent, get_gw_match_result


def players_performance_tab(player_info_df, player_stats_df, results_df):

    def create_ds(team, positions):
        """Returns DataFrame filtered team and positions.

        :param team: str. If 'None' is passed, all teams are selected.
        :param positions: list of str.
        :returns: DataFrame.
        """

        # Default Values
        SIZE = 8
        SIZES = [s for s in range(5, 38, 4)]
        COLOR = 'blueviolet'
        MAX_COLORS = len(Category20_20)

        if team == 'All':
            ds = pd.DataFrame(joined_player_df[
                                  joined_player_df['Position'].isin(
                                      positions)])
        else:
            ds = pd.DataFrame(joined_player_df[
                                  (joined_player_df['Position'].isin(
                                      positions)) &
                                  (joined_player_df['Team'] == team)])

        # Add sizes
        if size.value != 'None':
            if len(ds[size.value].unique()) > len(SIZES):
                groups = pd.qcut(ds[size.value].values,
                                 len(SIZES), duplicates='drop')
            else:
                groups = pd.Categorical(ds[size.value].values)

            ds['Size'] = np.array([SIZES[x] for x in groups.codes])

        else:
            ds['Size'] = SIZE

        # Add colors
        if color.value != 'None':
            if len(ds[color.value].unique()) > MAX_COLORS:
                groups = pd.qcut(ds[color.value].values,
                                 MAX_COLORS, duplicates='drop')
            else:
                groups = pd.Categorical(ds[color.value].values)

            ds['Color'] = np.array([Category20_20[x] for x in groups.codes])

        else:
            ds['Color'] = COLOR

        return ds

    def plot_stats():
        """Creates and returns a figure."""

        pos = [positions[i] for i in select_position.active]
        team = select_team.value
        ds = create_ds(team, pos)
        source = ColumnDataSource(ds)

        p = figure(plot_height=600, plot_width=800,
                   title=f'{x.value} vs {y.value}',
                   tools='pan,box_zoom,reset')

        p.circle(x=x.value, y=y.value, size='Size', color='Color',
                 alpha=0.5, source=source, hover_color='navy')

        hover = HoverTool(tooltips=[('Player', '@Name'),
                                    ('Team', '@Team'),
                                    (f'{x.value}', f'@{{{x.value}}}'),
                                    (f'{y.value}', f'@{{{y.value}}}'),
                                    (f'Opponent', f'@Opponent')])

        if size.value != 'None':
            hover.tooltips.append((f'{size.value}', f'@{{{size.value}}}'))
        if color.value != 'None':
            hover.tooltips.append((f'{color.value}', f'@{{{color.value}}}'))
        hover.point_policy = 'follow_mouse'

        p.add_tools(hover)
        p.xaxis.axis_label = x.value
        p.yaxis.axis_label = y.value

        return p

    def update(atrrname, old, new):
        layout.children[1] = plot_stats()

    # Create merged dataFrame of players stats and info
    joined_player_df = pd.merge(player_stats_df, player_info_df, on='pid',
                                how='inner')
    joined_player_df.drop(columns=['index_x'], inplace=True)
    # Add columns: result (w/l/d), opponent
    joined_player_df['Opponent'] = joined_player_df.apply(get_opponent,
                                                          args=[results_df],
                                                          axis=1)
    joined_player_df['Result'] = joined_player_df.apply(get_gw_match_result,
                                                        args=[results_df],
                                                        axis=1)

    # Data filtering widgets by Team and Position
    teams = ['All'] + sorted(list(player_info_df['Team'].unique()))
    select_team = Select(title='Filter by Team', value='All', options=teams)
    select_team.on_change('value', update)

    positions = ['GK', 'Defender', 'Midfielder', 'Forward']
    select_position = CheckboxButtonGroup(labels=positions,
                                          active=[0, 1, 2, 3])
    select_position.on_change('active', update)

    # Select stats to plot
    columns = [x for x in sorted(player_stats_df.columns)
               if x not in ['index', 'pid', 'Gameweek', 'Season']]
    x = Select(title='X Axis', value='Minutes', options=columns)
    x.on_change('value', update)
    y = Select(title='Y Axis', value='Passes', options=columns)
    y.on_change('value', update)
    size = Select(title='Add Size Dimension', value='None',
                  options=['None'] + columns)
    size.on_change('value', update)
    color = Select(title='Add Color Segmentation', value='None',
                   options=['None', 'Result', 'Gameweek', 'Position'])
    color.on_change('value', update)

    widgets = widgetbox([select_team, select_position, x, y, size, color])

    layout = row(widgets, plot_stats())
    tab = Panel(child=layout, title='Players Performances')

    return tab
