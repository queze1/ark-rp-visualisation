from dash import dcc
import dash_mantine_components as dmc

from frontend.controls import make_controls

EXPLAINER = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""


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
        dmc.Tabs(
            [
                dmc.TabsList(
                    [
                        dmc.TabsTab("Time Series", value="line"),
                        dmc.TabsTab("Bar", value="bar"),
                        dmc.TabsTab("Scatter", value="scatter"),
                    ]
                ),
                dmc.TabsPanel(make_controls("line"), value="line"),
                dmc.TabsPanel(make_controls("bar"), value="bar"),
                dmc.TabsPanel(make_controls("scatter"), value="scatter"),
            ],
            id="tabs",
            value="line",
        ),
        dcc.Graph(id="graph"),
        dcc.Store(id="graph-config"),
    ]
)
