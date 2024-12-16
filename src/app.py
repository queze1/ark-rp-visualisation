import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Output, Input

from backend.data_loader import DataLoader
from backend.plot_builder import PlotBuilder
from frontend.layout import layout

# df = DataLoader().load_data().df

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


# app.layout = [
#     html.H1("ARK RP Channel Visualisation"),
#     html.Hr(),
# ]

app.layout = layout


# @app.callback(Output("content", "children"), [Input("tabs", "active_tab")])
# def switch_tab(at):
#     if at == "tab-1":
#         return "test"
#     elif at == "tab-2":
#         return "test"
#     return html.P("This shouldn't ever be displayed...")


# @app.callback(
#     Output("rp-graph", "figure"),
#     [
#         Input("x-variable", "value"),
#         Input("y-variable", "value"),
#         Input("groupby", "value"),
#         Input("plot-type", "value"),
#     ],
# )
# def make_graph(x, y, groupby, plot_type):
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
