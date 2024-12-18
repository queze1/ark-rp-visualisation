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


# @app.callback(
#     Output("graph", "figure"),
#     [
#         Input("graph-config", "data"),
#     ],
# )
# def make_graph(config):
#     x, y, groupby, plot_type = config
#     if not (x and y and groupby and plot_type):
#         return {}

#     return (
#         PlotBuilder(df)
#         ._queue_add_field(x)
#         ._queue_add_field(y)
#         ._queue_group_by(GroupBy(groupby))
#         ._queue_build_plot(Plot(plot_type))
#         .build()
#         .figure
#     )


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
