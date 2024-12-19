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
    if tab == "line":
        return dbc.Col(
            [
                dbc.Label("Plot By"),
                make_field_dropdown(index=0, condition=is_valid_line),
            ]
        )
    elif tab == "bar":
        return dbc.Col(
            [
                dbc.Label("X-Axis"),
                make_field_dropdown(index=0, condition=is_valid_xbar),
                dbc.Label("Y-Axis"),
                make_field_dropdown(index=1),
            ]
        )
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
