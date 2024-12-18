import dash_bootstrap_components as dbc
from dash import ALL, Dash, Input, Output, State

from backend.data_loader import DataLoader
from frontend.controls import make_controls, make_dropdown_options
from frontend.layout import layout

df = DataLoader().load_data().df

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = layout


@app.callback(Output("control-div", "children"), Input("tabs", "active_tab"))
def update_controls(tab):
    return make_controls(tab)


@app.callback(
    Output({"type": "field-dynamic-dropdown", "index": ALL}, "options"),
    Input({"type": "field-dynamic-dropdown", "index": ALL}, "value"),
    State({"type": "field-dynamic-dropdown", "index": ALL}, "options"),
)
def update_dropdown_options(selected_values, current_options):
    return make_dropdown_options(selected_values, current_options)


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
