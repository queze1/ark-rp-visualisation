from dash import Dash, dcc, html, Input, Output, State, MATCH, Patch, callback

app = Dash()


app.layout = html.Div(
    [
        html.Button("Tab A", id={"type": "city-button", "tab": "a"}, n_clicks=0),
        html.Div(id={"type": "dropdown-container", "tab": "a"}, children=[]),
        html.Button("Tab B", id={"type": "city-button", "tab": "b"}, n_clicks=0),
        html.Div(id={"type": "dropdown-container", "tab": "b"}, children=[]),
    ]
)


@callback(
    Output({"type": "dropdown-container", "tab": MATCH}, "children"),
    Input({"type": "city-button", "tab": MATCH}, "n_clicks"),
    State({"type": "city-button", "tab": MATCH}, "id"),
)
def display_dropdowns(n_clicks, id):
    patched_children = Patch()

    tab = id["tab"]
    new_element = html.Div(
        [
            dcc.Dropdown(
                ["NYC", "MTL", "LA", "TOKYO"],
                id={"type": "city-dynamic-dropdown", "tab": tab, "index": n_clicks},
            ),
            html.Div(
                id={
                    "type": "city-dynamic-output",
                    "tab": id["tab"],
                    "index": n_clicks,
                }
            ),
        ]
    )
    patched_children.append(new_element)
    return patched_children


@callback(
    Output({"type": "city-dynamic-output", "tab": MATCH, "index": MATCH}, "children"),
    Input({"type": "city-dynamic-dropdown", "tab": MATCH, "index": MATCH}, "value"),
    State({"type": "city-dynamic-dropdown", "tab": MATCH, "index": MATCH}, "id"),
)
def display_output(value, id):
    return html.Div(f"Dropdown {id['index']} = {value}")


if __name__ == "__main__":
    app.run(debug=True)
