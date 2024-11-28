from dash import Dash, dcc, callback, Input, Output
from plots import PlotBuilderHelper

app = Dash(__name__)

# TODO: Make PlotBuilderHelper stateless
builder = PlotBuilderHelper()

graph_types = {
    "unique_authors_by_date_line": builder.unique_authors_by_date_line,
    "messages_by_date_line": builder.messages_by_date_line,
}

app.layout = [
    dcc.Dropdown(
        ["unique_authors_by_date_line", "messages_by_date_line"],
        id="rp-graph-type",
    ),
    dcc.Graph(id="rp-graph"),
]


@callback(Output("rp-graph", "figure"), Input("rp-graph-type", "value"))
def update_figure(type):
    if type is None:
        return {}

    return graph_types[type]().build()


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
