from urllib.parse import parse_qs, urlparse

from dash import Input, Output

from ark_rp_visualisation.core.enums import Page
from ark_rp_visualisation.pages.dashboard import layout as dashboard_layout
from ark_rp_visualisation.pages.fullscreen import layout as fullscreen_layout
from ark_rp_visualisation.pages.error import layout as error_layout
from ark_rp_visualisation.utils.serialisation import decode_state


def register_router_callbacks(app):
    def display_page(href):
        if not href:
            return dashboard_layout

        parsed_url = urlparse(href)

        # /graph: Fullscreen graph
        if parsed_url.path == "/graph":
            params = parse_qs(parsed_url.query)
            state_str = params.get("state", [None])[0]
            if not state_str:
                return error_layout("No graph URL")

            state = decode_state(state_str)
            if not state:
                return error_layout("Invalid graph URL")

            return fullscreen_layout(state)

        # /: Graph dashboard
        if parsed_url.path == "/":
            return dashboard_layout

        return error_layout("404 Not Found")

    app.callback(
        Output(Page.CONTENT, "children"),
        Input(Page.URL, "href"),
    )(display_page)
