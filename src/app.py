import dash_mantine_components as dmc
from dash import ALL, Dash, Input, Output, State, _dash_renderer

from backend.data_loader import DataLoader
from frontend.controls import make_controls, make_dropdown_options
from frontend.layout import layout

_dash_renderer._set_react_version("18.2.0")

df = DataLoader().load_data().df

app = Dash(external_stylesheets=dmc.styles.ALL)
app.layout = dmc.MantineProvider(layout)


@app.callback(Output("controls", "children"), Input("tabs", "value"))
def update_controls(tab):
    return make_controls(tab)


@app.callback(
    Output({"type": "field-dynamic-dropdown", "index": ALL}, "data"),
    Input({"type": "field-dynamic-dropdown", "index": ALL}, "value"),
    State({"type": "field-dynamic-dropdown", "index": ALL}, "data"),
)
def update_dropdown_options(selected_values, current_options):
    return make_dropdown_options(selected_values, current_options)


if __name__ == "__main__":
    app.run_server(debug=True)
