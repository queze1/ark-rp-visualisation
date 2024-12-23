import dash_mantine_components as dmc
from dash import dcc

from dashboard.fields import make_field_controls
from dashboard.filters import make_filter_controls
from enums import Page, Tab, Text


def make_tab(tab: Tab):
    return dmc.Card(
        [
            make_field_controls(tab),
            dmc.Divider(my=25),
            make_filter_controls(tab),
            dmc.Space(h=20),
            dmc.Button(
                Text.UPDATE_GRAPH_LABEL,
                ml="auto",
                maw=200,
                id={"type": Page.UPDATE_GRAPH_BUTTON, "tab": tab},
            ),
            dmc.Space(h=20),
            dcc.Graph(
                id={"type": Page.GRAPH, "tab": tab},
            ),
        ],
        withBorder=True,
    )
