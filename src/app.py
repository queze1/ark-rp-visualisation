import dash_mantine_components as dmc
from dash import Dash, _dash_renderer

from data_loader import DataLoader
from enums import PageText
from frontend.callbacks import register_callbacks
from frontend.layout import layout

_dash_renderer._set_react_version("18.2.0")

df = DataLoader().load_data().df

app = Dash(external_stylesheets=dmc.styles.ALL)
app.title = PageText.TITLE
app.layout = dmc.MantineProvider(layout)
register_callbacks(app)


if __name__ == "__main__":
    app.run_server(debug=True)
