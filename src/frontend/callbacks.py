from enums import Tab, Field, Page

from dash import ALL, Input, Output, State
from data_loader import DataLoader
from frontend.plot import PlotBuilder

df = DataLoader().load_data().df


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

    def process_option(dropdown_index, opt):
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
        [process_option(i, opt) for opt in options]
        for i, options in enumerate(current_options)
    ]


def render_graph(n_clicks, selected_fields, tab_id):
    y_field, x_field = selected_fields
    if not (n_clicks and x_field and y_field):
        return {}

    return PlotBuilder(df).plot(
        primary_field=x_field,
        secondary_field=y_field,
        x_axis=x_field,
        y_axis=y_field,
        plot_type=tab_id,
    )


def register_callbacks(app):
    for tab in Tab:
        app.callback(
            Output({"type": Page.FIELD_DROPDOWN(tab), "index": ALL}, "data"),
            Input({"type": Page.FIELD_DROPDOWN(tab), "index": ALL}, "value"),
            State({"type": Page.FIELD_DROPDOWN(tab), "index": ALL}, "data"),
        )(update_dropdown_options)
        app.callback(
            Output(Page.GRAPH(tab), "figure"),
            Input(Page.SUBMIT_BUTTON(tab), "n_clicks"),
            State({"type": Page.FIELD_DROPDOWN(tab), "index": ALL}, "value"),
            State(Page.TABS, "value"),
        )(render_graph)
