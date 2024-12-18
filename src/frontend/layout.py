from dash import dcc, html
import dash_bootstrap_components as dbc
from pipeline.enums import Field, GroupBy


EXPLAINER = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""

controls = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("X variable"),
                dcc.Dropdown(
                    id="x-variable",
                    options=[{"label": field, "value": field} for field in Field],
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("Y variable"),
                dcc.Dropdown(
                    id="y-variable",
                    options=[{"label": field, "value": field} for field in Field],
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("Groupby"),
                dcc.Dropdown(
                    id="groupby",
                    options=[
                        {"label": groupby, "value": groupby} for groupby in GroupBy
                    ],
                ),
            ]
        ),
    ],
    body=True,
)

layout = dbc.Container(
    [
        html.H1("ARK RP Channel Visualisation"),
        dcc.Markdown(EXPLAINER),
        dbc.Tabs(
            [
                dbc.Tab(label="Time Series", tab_id="line"),
                dbc.Tab(label="Bar", tab_id="bar"),
                dbc.Tab(label="Scatter", tab_id="scatter"),
            ],
            id="tabs",
            active_tab="line",
        ),
        dbc.Row(
            [
                dbc.Col(controls),
                dbc.Col(dcc.Graph(id="graph")),
            ],
            align="center",
        ),
        dcc.Store(id="graph-config"),
    ]
)
