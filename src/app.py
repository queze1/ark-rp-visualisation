from dash import Dash, dcc

app = Dash(__name__)

app.layout = [
    dcc.Graph(id="rp-graph"),
]

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
