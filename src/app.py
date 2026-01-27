import dash_mantine_components as dmc
from dash import Dash, _dash_renderer

from core.enums import Text
from layout import layout
from pages.dashboard import register_dashboard_callbacks
from router import register_router_callbacks

# Required for DMC
_dash_renderer._set_react_version("18.2.0")

app = Dash(external_stylesheets=dmc.styles.ALL, prevent_initial_callbacks=True)  # type: ignore
app.title = Text.TITLE
app.layout = layout

# Expose Flask server to Gunicorn
server = app.server

register_router_callbacks(app)
register_dashboard_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)
