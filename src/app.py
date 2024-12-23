import dash_mantine_components as dmc
from dash import Dash, _dash_renderer

from enums import Text
from dashboard.callbacks import register_callbacks
from dashboard.layout import layout

_dash_renderer._set_react_version("18.2.0")


app = Dash(external_stylesheets=dmc.styles.ALL, prevent_initial_callbacks=True)
app.title = Text.TITLE
app.layout = dmc.MantineProvider(layout)
register_callbacks(app)


if __name__ == "__main__":
    app.run_server(debug=True)
