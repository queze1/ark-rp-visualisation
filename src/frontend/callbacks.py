from enums import Field, Page, Text

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

    # Generate a list of patches, one for each output from the pattern-match
    return [
        process_options(selected_field, options)
        for selected_field, options in zip(selected_fields, current_options)
    ]


def swap_axes(n_clicks, axes_text):
    if not n_clicks:
        return axes_text

    left, right = axes_text
    return [right, left]


def render_graph(n_clicks, selected_fields, axes_text, id):
    if not (n_clicks and all(selected_fields)):
        return {}

    primary_field, secondary_field, *_ = selected_fields
    # Check axes labels
    if axes_text == [Text.Y_AXIS, Text.X_AXIS]:
        axes = dict(y_axis=primary_field, x_axis=secondary_field)
    elif axes_text == [Text.X_AXIS, Text.Y_AXIS]:
        axes = dict(x_axis=primary_field, y_axis=secondary_field)
    else:
        raise ValueError("Invalid axes")

    return PlotBuilder(df).plot(
        fields=selected_fields,
        plot_type=id["tab"],
        **axes,
    )

    # secondary_field, primary_field = selected_fields
    # if not (n_clicks and primary_field and secondary_field):
    #     return {}

    # # Check axes labels
    # if axes_text == [Text.Y_AXIS, Text.X_AXIS]:
    #     axes = dict(y_axis=secondary_field, x_axis=primary_field)
    # elif axes_text == [Text.X_AXIS, Text.Y_AXIS]:
    #     axes = dict(x_axis=secondary_field, y_axis=primary_field)
    # else:
    #     raise ValueError("Invalid axes")

    # return PlotBuilder(df).plot(
    #     primary_field=primary_field,
    #     secondary_field=secondary_field,
    #     plot_type=id["tab"],
    #     **axes,
    # )


def register_callbacks(app):
    app.callback(
        Output({"type": Page.FIELD_DROPDOWN, "tab": MATCH, "index": ALL}, "data"),
        Input({"type": Page.FIELD_DROPDOWN, "tab": MATCH, "index": ALL}, "value"),
        State({"type": Page.FIELD_DROPDOWN, "tab": MATCH, "index": ALL}, "data"),
    )(update_dropdown_options)
    app.callback(
        Output({"type": Page.AXIS_TEXT, "tab": MATCH, "index": ALL}, "children"),
        Input({"type": Page.SWAP_AXES_BUTTON, "tab": MATCH}, "n_clicks"),
        State({"type": Page.AXIS_TEXT, "tab": MATCH, "index": ALL}, "children"),
    )(swap_axes)
    app.callback(
        Output({"type": Page.GRAPH, "tab": MATCH}, "figure"),
        Input({"type": Page.UPDATE_GRAPH_BUTTON, "tab": MATCH}, "n_clicks"),
        State({"type": Page.FIELD_DROPDOWN, "tab": MATCH, "index": ALL}, "value"),
        State({"type": Page.AXIS_TEXT, "tab": MATCH, "index": ALL}, "children"),
        State({"type": Page.UPDATE_GRAPH_BUTTON, "tab": MATCH}, "id"),
    )(render_graph)
