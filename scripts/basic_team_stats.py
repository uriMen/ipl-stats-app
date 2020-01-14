#! python 3
# basic_team_stats.py - create tab for bokeh app
# with basic teams statistics.

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, Panel
from bokeh.models.ranges import FactorRange
from bokeh.models.widgets import Select, RadioButtonGroup
from bokeh.transform import dodge
from bokeh.models import Legend
from bokeh.layouts import column, row, widgetbox
from bokeh.palettes import Spectral4


def basic_teams_stats_tab(teams_stats_df):
    """Tab with teams stats."""

    def create_data_source(comparison_stat, aggfunc):
        """Returns a pivoted table by teams and match result (w/d/l).

        Values are index of comparison_stat.

        :param comparison_stat: str. Statistic to show (goals, passes,
        etc.).
        :param aggfunc: str. Aggregate function to calculate by ('mean'
         or 'sum').
        """

        def get_team_indexed_stat(team_row, stat, aggfunc):
            """Returns aggregated team's stat.

            :param team_row: pd.Series. A row from teams stat table.
            :param stat: str. Statistic to calculate (goal, passes,
            etc.)
            :param aggfunc: str. Aggregate function to calculate by
            ('mean' or 'sum')
            """

            if aggfunc == 'mean':
                df = teams_stats_df.groupby(by='team').mean()
            elif aggfunc == 'sum':
                df = teams_stats_df.groupby(by='team').sum()
            return df.loc[team_row.name, stat]

        df = teams_stats_df.pivot_table(
            index='team',
            columns='Match result',
            values=comparison_stat,
            aggfunc=aggfunc)

        df['Total'] = df.apply(get_team_indexed_stat,
                               args=[comparison_stat, aggfunc], axis=1)

        return df.sort_values(by='Total', ascending=False)

    def plot_team_stat(comparison_stat, agg_func):
        """Creates figures with bars plots of teams stats.

        :param comparison_stat: str. Statistic to plot.
        :param agg_func: str. 'mean' or 'sum'.
        :return: bokeh figures.
        """

        map_agg_func = ('mean', 'sum')
        data = create_data_source(comparison_stat, map_agg_func[agg_func])
        source = ColumnDataSource(data=data)
        teams = list(source.data['team'])

        # Plot avg stat per game

        p_1 = figure(x_range=FactorRange(factors=teams), plot_height=400,
                     plot_width=700)

        hover = HoverTool(tooltips=[('', '@{Total}')])
        hover.point_policy = 'follow_mouse'
        p_1.add_tools(hover)

        p_1.vbar(x='team', top='Total', source=source, width=0.4,
                 color=Spectral4[0])

        p_1.x_range.range_padding = 0.05
        p_1.xaxis.major_label_orientation = 1
        p_1.xaxis.major_label_text_font_size = "10pt"
        p_1.toolbar_location = None

        # Plot breakdown by match result

        p_2 = figure(x_range=FactorRange(factors=teams), plot_height=400,
                     plot_width=700, tools='hover', tooltips='@$name',
                     title='Breakdown by Match Result')

        w = p_2.vbar(x=dodge('team', -0.25, range=p_2.x_range), top='w',
                     width=0.2, source=source, color=Spectral4[1], name='w')
        d = p_2.vbar(x=dodge('team', 0.0, range=p_2.x_range), top='d',
                     width=0.2, source=source, color=Spectral4[2], name='d')
        l = p_2.vbar(x=dodge('team', 0.25, range=p_2.x_range), top='l',
                     width=0.2, source=source, color=Spectral4[3], name='l')

        legend_it = [('Won', [w]), ('Drew', [d]), ('Lost', [l])]
        legend = Legend(items=legend_it, location=(0, 155))

        p_2.add_layout(legend, 'right')
        p_2.title.text_font_size = '12pt'
        p_2.x_range.range_padding = 0.05
        p_2.xgrid.grid_line_color = None
        p_2.xaxis.major_label_text_font_size = "10pt"
        p_2.xaxis.major_label_orientation = 1
        p_2.toolbar_location = None

        return p_1, p_2

    # Update plots on changes

    def update(attrname, old, new):
        """Update plots after widgets changes."""
        stat = select_stat.value
        agg_func = choose_agg_func.active
        p1, p2 = plot_team_stat(stat, agg_func)
        layout.children[1:] = [p1, p2]

    # Widgets
    select_stat = Select(title="Select a Stat for Comparison:", value="goal",
                         options=list(teams_stats_df.columns)[1:-3])
    select_stat.on_change('value', update)

    choose_agg_func = RadioButtonGroup(labels=['Average per Match', 'Total'],
                                       active=0)
    choose_agg_func.on_change('active', update)

    # Wrap widgets
    widgets = widgetbox([select_stat, choose_agg_func])

    comparison_stat = select_stat.value
    agg_func_state = choose_agg_func.active

    # Arrange layout
    p1, p2 = plot_team_stat(comparison_stat, agg_func_state)
    layout = column(row(widgets), p1, p2)
    tab = Panel(child=layout, title='Basic Teams Stats')

    return tab
