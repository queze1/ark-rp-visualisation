import dash_mantine_components as dmc
from dash import Dash, _dash_renderer

from data_loader import DataLoader
from frontend.layout import layout
from frontend.controls import register_controls_callbacks

_dash_renderer._set_react_version("18.2.0")

df = DataLoader().load_data().df

app = Dash(external_stylesheets=dmc.styles.ALL)
app.layout = dmc.MantineProvider(layout)

# Add callbacks to the panels
register_controls_callbacks(app, "line")
register_controls_callbacks(app, "bar")
register_controls_callbacks(app, "scatter")


if __name__ == "__main__":
    app.run_server(debug=True)
