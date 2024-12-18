import dash_bootstrap_components as dbc
from dash import Dash, Output, Input

from backend.data_loader import DataLoader
from frontend.layout import layout
# from backend.enums import GroupBy, Plot

df = DataLoader().load_data().df

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = layout


@app.callback(
    Output("graph-config", "data"),
    [
        Input("x-variable", "value"),
        Input("y-variable", "value"),
        Input("groupby", "value"),
        Input("tabs", "active_tab"),
    ],
)
def set_graph_config(x, y, groupby, tab):
    return (x, y, groupby, tab)


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
