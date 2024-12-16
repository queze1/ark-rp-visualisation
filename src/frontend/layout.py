from dash import dcc, html
import dash_bootstrap_components as dbc


EXPLAINER = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""

layout = dbc.Container(
    [
        html.H1("ARK RP Channel Visualisation"),
        dcc.Markdown(EXPLAINER),
        dbc.Tabs(
            [
                dbc.Tab(label="Scatter", tab_id="scatter"),
                dbc.Tab(label="Histograms", tab_id="histogram"),
            ],
            id="tabs",
            active_tab="scatter",
        ),
        # we wrap the store and tab content with a spinner so that when the
        # data is being regenerated the spinner shows. delay_show means we
        # don't see the spinner flicker when switching tabs
        # dbc.Spinner(
        #     [
        #         dcc.Store(id="store"),
        #         html.Div(id="tab-content", className="p-4"),
        #     ],
        #     delay_show=100,
        # ),
    ]
)
