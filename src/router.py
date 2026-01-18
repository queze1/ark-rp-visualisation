from urllib.parse import parse_qs, urlparse

import dash_mantine_components as dmc
from dash import Input, Output

from dashboard.layout import footer, header, tabs
from utils.serialisation import decode_state
from dashboard.fullscreen_layout import make_fullscreen_layout
from enums import Page


def register_router_callbacks(app):
    def display_page(href):
        if not href:
            return dict(content=[header, tabs, footer], fluid=False)

        parsed_url = urlparse(href)

        # /graph: Fullscreen graph
        if parsed_url.path == "/graph":
            params = parse_qs(parsed_url.query)
            state_str = params.get("state", [None])[0]

            if not state_str:
                return dict(content=dmc.Alert("No graph URL", color="red"), fluid=False)

            state = decode_state(state_str)

            if not state:
                return dict(
                    content=dmc.Alert("Invalid graph URL", color="red"), fluid=False
                )

            return dict(content=make_fullscreen_layout(state), fluid=True)

        # /: Graph dashboard
        return dict(content=[header, tabs, footer], fluid=False)

    app.callback(
        Input(Page.URL, "href"),
        output=dict(
            content=Output(Page.CONTENT, "children"),
            fluid=Output(Page.CONTAINER, "fluid"),
        ),
    )(display_page)
