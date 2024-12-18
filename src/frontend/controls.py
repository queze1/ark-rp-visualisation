from backend.enums import Field
import dash_bootstrap_components as dbc
from dash import dcc


field_options = [
    {"label": field.label, "value": field} for field in Field if field.has_metadata
]


def make_controls(tab):
    if tab == "line":
        return dbc.Col(
            [
                dbc.Label("X-Axis"),
                dcc.Dropdown(
                    id={"type": "field-dynamic-dropdown", "index": 0},
                    options=field_options,
                    searchable=False,
                ),
                dbc.Label("Y-Axis"),
                dcc.Dropdown(
                    id={"type": "field-dynamic-dropdown", "index": 1},
                    options=field_options,
                    searchable=False,
                ),
            ]
        )
    return None


def make_dropdown_options(selected_values, current_options):
    # `selected_values` contains the current value of each dropdown
    # Disable selected values in all other dropdowns
    new_options = []
    for i, options in enumerate(current_options):
        updated_options = [
            {
                "label": opt["label"],
                "value": opt["value"],
                "disabled": opt["value"] in selected_values
                and opt["value"] != selected_values[i],
            }
            for opt in options
        ]
        new_options.append(updated_options)
    return new_options
