from enums import Field, Page

from dash import ALL, Input, Output, State, MATCH, Patch
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

    def process_options(selected_field, options):
        def process_option(opt):
            field = Field(opt["value"])

            # Check if field is already selected in another dropdown
            is_duplicate = field in selected_fields and field != selected_field

            # Check if this dropdown has selected a temporal field
            selected_temporal = (
                Field(selected_field).temporal if selected_field else False
            )
            is_invalid_temporal = (
                field.temporal and has_selected_temporal and not selected_temporal
            )

            return {
                "disabled": is_duplicate or is_invalid_temporal,
            }

        patched_options = Patch()
        for i, opt in enumerate(options):
            patched_options[i].update(process_option(opt))
        return patched_options

    return [
        process_options(selected_field, options)
        for selected_field, options in zip(selected_fields, current_options)
    ]


def render_graph(n_clicks, selected_fields, id):
    y_field, x_field = selected_fields
    if not (n_clicks and x_field and y_field):
        return {}

    return PlotBuilder(df).plot(
        primary_field=x_field,
        secondary_field=y_field,
        x_axis=x_field,
        y_axis=y_field,
        plot_type=id["tab"],
    )


def register_callbacks(app):
    app.callback(
        Output({"type": Page.FIELD_DROPDOWN, "tab": MATCH, "index": ALL}, "data"),
        Input({"type": Page.FIELD_DROPDOWN, "tab": MATCH, "index": ALL}, "value"),
        State({"type": Page.FIELD_DROPDOWN, "tab": MATCH, "index": ALL}, "data"),
    )(update_dropdown_options)
    app.callback(
        Output({"type": Page.GRAPH, "tab": MATCH}, "figure"),
        Input({"type": Page.SUBMIT_BUTTON, "tab": MATCH}, "n_clicks"),
        State({"type": Page.FIELD_DROPDOWN, "tab": MATCH, "index": ALL}, "value"),
        State({"type": Page.SUBMIT_BUTTON, "tab": MATCH}, "id"),
    )(render_graph)
