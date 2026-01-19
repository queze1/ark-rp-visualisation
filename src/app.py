import dash_mantine_components as dmc
from dash import Dash, _dash_renderer

from pages.dashboard import register_dashboard_callbacks, layout
from core.enums import Text

_dash_renderer._set_react_version("18.2.0")

app = Dash(external_stylesheets=dmc.styles.ALL, prevent_initial_callbacks=True)  # type: ignore
app.title = Text.TITLE
app.layout = dmc.MantineProvider(layout)

register_dashboard_callbacks(app)

server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
