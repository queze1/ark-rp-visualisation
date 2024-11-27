from dash import Dash, html, dcc
from plots import PlotBuilderHelper

app = Dash(__name__)


def generate_sample_plot():
    builder = PlotBuilderHelper()
    return builder.messages_by_date_line().build()


app.layout = html.Div(
    children=[
        html.H1("Hello World!"),
        html.P("Sample plot generated with PlotBuilder."),
        dcc.Graph(figure=generate_sample_plot()),
    ]
)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
