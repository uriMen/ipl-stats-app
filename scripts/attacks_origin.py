#! python 3
# attacks_origin.py - create tab for bokeh app
# with attacks statistics.

from math import pi

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Panel
from bokeh.models.widgets import Select, Div
from bokeh.layouts import column, row
from bokeh.palettes import Viridis
from bokeh.transform import cumsum


def attacks_origin_tab(team_stats_df):
    """Tab with attacks origins plots."""

    def create_ds_for_attacks_origin(team, with_shot=False,
                                     opp_attacks=False):
        """Collects stats about attack origins. Returns DataFrame.

        :param team: str.
        :param with_shot: bool. If True, collects stats about attacks
        ended with a shot.
        :param opp_attacks: bool. If True, collects stats of attacks
        against the given team.
        :return: pd.DataFrame. Number of attacks segmented by origin
        (left, right, center).
        """

        if opp_attacks:
            col_of_interest = 'Opponent'
        else:
            col_of_interest = 'Team'

        df = team_stats_df.groupby(by=col_of_interest).sum()
        df.reset_index(inplace=True)

        cols = {'total': ['Left Flank Attacks',
                          'Right Flank Attacks',
                          'Center Flank Attacks'],
                'with_shot': ['Left Flank Attacks With Shot',
                              'Right Flank Attacks With Shot',
                              'Center Flank Attacks With Shot']}
        cols_map = {'Left Flank Attacks': 'Left Field',
                    'Right Flank Attacks': 'Right Field',
                    'Center Flank Attacks': 'Center',
                    'Left Flank Attacks With Shot': 'Left Field',
                    'Right Flank Attacks With Shot': 'Right Field',
                    'Center Flank Attacks With Shot': 'Center'}
        if with_shot:
            data = df[df[col_of_interest] == team][
                cols['with_shot']].reset_index(drop=True)
        else:
            data = df[df[col_of_interest] == team][cols['total']].reset_index(
                drop=True)

        data.rename(mapper=cols_map, axis=1, inplace=True)
        ds = data.transpose().rename(columns={0: 'value'})
        ds['angle'] = ds['value'] / ds['value'].sum() * 2 * pi
        ds['color'] = Viridis[len(ds)]
        return ds

    def plot_attacks_by_origin(team, opp_attacks=False):
        """Plots data of attacks segmented by origin of attack.

        Total num of attacks in a pie chart. Attacks ended with a shot
        in bars.

        :param team: str.
        :param opp_attacks: bool. If True, collects stats of attacks
        against the given team.
        """
        # Plot attack in pie chart
        data_pc = create_ds_for_attacks_origin(team, with_shot=False,
                                               opp_attacks=opp_attacks)
        #         print(data_pc.head(2))
        source_pc = ColumnDataSource(data_pc)

        pc = figure(plot_height=300, plot_width=300, title="Attacks Origins",
                    toolbar_location=None, tools="hover",
                    tooltips="@index: @value", x_range=(-0.5, 1))

        pc.wedge(x=0, y=1, radius=0.4,
                 start_angle=cumsum('angle', include_zero=True),
                 end_angle=cumsum('angle'), line_color="white",
                 fill_color='color', legend='index', source=source_pc)

        pc.axis.axis_label = None
        pc.axis.visible = False
        pc.grid.grid_line_color = None

        # Plot attacks ended with a shot
        data_with_shot = create_ds_for_attacks_origin(team, with_shot=True,
                                                      opp_attacks=opp_attacks)
        attack_origin = ['Left Field', 'Center', 'Right Field']
        source = ColumnDataSource(data_with_shot)

        p = figure(plot_height=300, plot_width=300,
                   title="Attacks Ended With a Shot",
                   toolbar_location=None, tools="hover",
                   tooltips="@index: @value", x_range=attack_origin)

        p.vbar(x='index', top='value', fill_color='color', width=0.5,
               source=source)

        p.grid.grid_line_color = None
        p.xaxis.major_label_text_font_size = "10pt"
        p.axis.axis_line_color = None
        p.xaxis.major_tick_line_color = None
        p.yaxis.minor_tick_line_color = None

        return pc, p

    def update_team(atrrname, old, new):
        team = select_team.value
        p1, p2 = plot_attacks_by_origin(team)
        p3, p4 = plot_attacks_by_origin(team, opp_attacks=True)
        layout.children[1::2] = [row(p1, p2), row(p3, p4)]

    # Select-Team widget
    teams = sorted(list(team_stats_df['Team'].unique()))
    select_team = Select(title='Select a Team', value='Beitar Jerusalem',
                         options=teams)

    team = select_team.value
    select_team.on_change('value', update_team)

    # Separation paragraph
    counter_attack_sep = Div(text="<b>Opponents Attacks</b>",
                             style={'font-size': '170%', 'color': 'grey'})

    # Arrange layout
    p1, p2 = plot_attacks_by_origin(team)
    p3, p4 = plot_attacks_by_origin(team, opp_attacks=True)
    layout = column(row(select_team), row(p1, p2),
                    counter_attack_sep, row(p3, p4))
    tab = Panel(child=layout, title='Attacks Origins')

    return tab
