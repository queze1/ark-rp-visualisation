import dash_mantine_components as dmc
from dash import dcc

from core import PlotBuilder
from core.enums import PlotType, Tab, Text
from core.models import AxisConfig, FigureConfig, FilterConfig


def make_layout(state: dict):
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
