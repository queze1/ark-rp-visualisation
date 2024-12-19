from backend.enums import Field
import dash_bootstrap_components as dbc
from dash import dcc, html


def make_controls(tab):
    def make_field_text(text):
        return html.P(text, style={"font-size": "1.2rem"})

    def make_field_dropdown(index, condition=lambda _: True, **kwargs):
        return dcc.Dropdown(
            id={"type": "field-dynamic-dropdown", "index": index},
            options=[
                {"label": field.label, "value": field}
                for field in Field
                if field.label and condition(field)
            ],
            searchable=False,
            clearable=False,
            **kwargs,
        )

    def make_axis_text(text):
        return html.P(text, style={"text-align": "center", "margin-top": 2})

    def make_field_controls(field_options):
        return dbc.Row(
            [
                dbc.Col(make_field_text("Plot"), width="auto"),
                dbc.Col(
                    [
                        make_field_dropdown(index=0, **field_options[0]),
                        make_axis_text("Y-Axis"),
                    ],
                    width=2,
                ),
                dbc.Col(make_field_text("By"), width="auto"),
                dbc.Col(
                    [
                        make_field_dropdown(index=1, **field_options[1]),
                        make_axis_text("X-Axis"),
                    ],
                    width=2,
                ),
            ],
            className="g-3",
            justify="center",
        )

    def make_filter_controls():
        return dbc.Stack(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.P("Filters", style={"font-size": "1.25rem"}),
                            width="auto",
                        ),
                        dbc.Col(
                            html.P("Reset"),
                            width="auto",
                        ),
                    ],
                    justify="between",
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Date")),
                        dbc.Col(dcc.DatePickerRange()),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("User")),
                        dbc.Col(
                            dcc.Dropdown(
                                ["New York City", "Montreal", "San Francisco"],
                                value=None,
                                multi=True,
                            )
                        ),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Channel Name")),
                        dbc.Col(
                            dcc.Dropdown(
                                ["New York City", "Montreal", "San Francisco"],
                                value=None,
                                multi=True,
                            )
                        ),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Hour")),
                        dbc.Col(dcc.RangeSlider(0, 23, 1)),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label("Reaction Count")),
                        dbc.Col(
                            dcc.Dropdown(["<", "=", ">", "<=", ">="]),
                        ),
                        dbc.Col(
                            dbc.Input(
                                type="number",
                                min=0,
                                step=1,
                                placeholder="Enter number...",
                            ),
                        ),
                    ],
                ),
            ],
            gap=2,
        )

    tab_fields = [
        {
            "condition": lambda field: not field.temporal,
        },
        {
            "value": Field.DATE,
            "condition": lambda field: field is Field.DATE,
        },
    ]
    bar_fields = [{"condition": lambda field: field is not Field.DATE}, {}]
    if tab == "line":
        return [make_field_controls(tab_fields), html.Hr(), make_filter_controls()]
    elif tab == "bar":
        return [make_field_controls(bar_fields), html.Hr(), make_filter_controls()]
    return None


def make_dropdown_options(selected_fields, current_options):
    """
    Rules:
    1. No duplicate options.
    2. No more than one temporal field.
    """

    # Check if any temporal field is already selected
    has_selected_temporal = any(
        [Field(field).temporal if field else None for field in selected_fields]
    )

    def process_option(opt, dropdown_index):
        label, field = opt["label"], Field(opt["value"])

        # Check if field is already selected in another dropdown
        is_duplicate = (
            field in selected_fields and field != selected_fields[dropdown_index]
        )

        # Check if this dropdown has selected a temporal field
        selected_temporal = (
            Field(selected_fields[dropdown_index]).temporal
            if selected_fields[dropdown_index]
            else False
        )
        is_invalid_temporal = (
            field.temporal and has_selected_temporal and not selected_temporal
        )

        return {
            "label": label,
            "value": field,
            "disabled": is_duplicate or is_invalid_temporal,
        }

    return [
        [process_option(opt, i) for opt in options]
        for i, options in enumerate(current_options)
    ]
