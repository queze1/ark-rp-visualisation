import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Output, Input

from backend.data_loader import DataLoader
from backend.plot_builder import PlotBuilder
from backend.enums import Field, GroupBy, Plot
from frontend.layout import layout

# df = DataLoader().load_data().df

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# controls = dbc.Card(
#     [
#         html.Div(
#             [
#                 dbc.Label("X variable"),
#                 dcc.Dropdown(
#                     id="x-variable",
#                     options=[{"label": field, "value": field} for field in Field],
#                 ),
#             ]
#         ),
#         html.Div(
#             [
#                 dbc.Label("Y variable"),
#                 dcc.Dropdown(
#                     id="y-variable",
#                     options=[{"label": field, "value": field} for field in Field],
#                 ),
#             ]
#         ),
#         html.Div(
#             [
#                 dbc.Label("Groupby"),
#                 dcc.Dropdown(
#                     id="groupby",
#                     options=[
#                         {"label": groupby, "value": groupby} for groupby in GroupBy
#                     ],
#                 ),
#             ]
#         ),
#         html.Div(
#             [
#                 dbc.Label("Plot Type"),
#                 dcc.Dropdown(
#                     id="plot-type",
#                     options=[{"label": plot, "value": plot} for plot in Plot],
#                 ),
#             ]
#         ),
#     ],
#     body=True,
# )

# app.layout = [
#     html.H1("ARK RP Channel Visualisation"),
#     html.Hr(),
#     dbc.Row(
#         [
#             dbc.Col(controls, md=4),
#             dbc.Col(dcc.Graph(id="rp-graph"), md=8),
#         ],
#         align="center",
#     ),
# ]

app.layout = layout


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
