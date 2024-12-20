from enums import Tab, Field

from dash import ALL, Input, Output, State


def update_dropdown_options(selected_fields, current_options):
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


def register_callbacks(app):
    for tab in Tab:
        app.callback(
            Output({"type": f"{tab}-field-dropdown", "index": ALL}, "data"),
            Input({"type": f"{tab}-field-dropdown", "index": ALL}, "value"),
            State({"type": f"{tab}-field-dropdown", "index": ALL}, "data"),
        )(update_dropdown_options)
