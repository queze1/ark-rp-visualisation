import dash_mantine_components as dmc
from dash import dcc

from frontend import EXPLAINER, TABS
from frontend.tabs import make_tabs

layout = dmc.Container(
    [
        dmc.Stack(
            [
                dmc.Title("ARK RP Channel Visualisation"),
                dmc.Text(EXPLAINER),
            ],
            mt=10,
            mb=20,
            gap=10,
        ),
        make_tabs(TABS, "line"),
        dcc.Graph(id="graph"),
    ]
)
