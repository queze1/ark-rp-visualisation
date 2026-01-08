import dash_mantine_components as dmc
from dash import dcc

from dashboard.graph_engine import PlotBuilder
from dashboard.models import AxisConfig, FigureConfig, FilterConfig
from enums import PlotType, Tab, Text


def make_fullscreen_layout(state: dict):
    active_tab = Tab(state["tab"])
    fig = PlotBuilder(
        plot_type=PlotType(active_tab.plot_type),
        axis_config=AxisConfig.from_raw(state["fields"], state["axes"], state["aggs"]),
        filter_config=FilterConfig.from_raw(*state["filters"]),
        figure_config=FigureConfig.from_raw(**state["custom"]),
    ).build()

    return dmc.Container(
        [
            dmc.Anchor(
                Text.TITLE,
                href="/",
                underline=False,
                style={
                    "fontSize": "20px",
                    "fontWeight": "bold",
                    "color": "black",
                },
            ),
            dcc.Graph(
                figure=fig,
                style={"height": "95vh"},
            ),
        ],
        fluid=True,
    )
