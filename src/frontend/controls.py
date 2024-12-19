from backend.enums import Field
import dash_bootstrap_components as dbc
from dash import dcc


def is_valid_line(field: Field):
    return not field.temporal


def is_valid_xbar(field: Field):
    return field is not Field.DATE


def make_field_dropdown(index, condition=lambda _: True):
    return dcc.Dropdown(
        id={"type": "field-dynamic-dropdown", "index": index},
        options=[
            {"label": field.label, "value": field}
            for field in Field
            if field.label and condition(field)
        ],
        searchable=False,
    )


def make_controls(tab):
    def make_fields(rows):
        """
        Parameters:
            rows (list of dict): Each dict defines a row with the following keys:
                - label (str): The label text for the row.
                - dropdown_params (dict): Parameters for the `make_field_dropdown` function.

        Returns:
            dbc.Stack: The generated layout.
        """
        return dbc.Stack(
            [
                dbc.Row(
                    [
                        dbc.Col(dbc.Label(row["label"])),
                        dbc.Col(make_field_dropdown(index=i, **row["dropdown_params"])),
                    ]
                )
                for i, row in enumerate(rows)
            ],
            gap=2,
        )

    line_fields = [
        {"label": "Plot By", "dropdown_params": {"condition": is_valid_line}}
    ]
    bar_fields = [
        {"label": "X-Axis", "dropdown_params": {"condition": is_valid_xbar}},
        {"label": "Y-Axis", "dropdown_params": {}},
    ]

    if tab == "line":
        return make_fields(line_fields)
    elif tab == "bar":
        return make_fields(bar_fields)
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
