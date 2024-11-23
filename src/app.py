from dash import Dash, html

app = Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1("Hello World!"),
    ]
)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
