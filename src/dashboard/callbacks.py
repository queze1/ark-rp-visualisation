from enums import Field, Filter, Page, Text, Tab

from dash import ALL, Input, Output, State, MATCH, Patch, ctx
from data_loader import df
from dashboard.plot import PlotBuilder


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


def swap_axes(n_clicks, axes):
    if n_clicks is None:
        return axes

    left, right = axes
    return [right, left]


def render_graph(
    n_clicks,
    selected_fields,
    selected_axes,
    filter_operators,
    filter_values,
):
    if n_clicks is None or not all(selected_fields):
        return {}

    print(filter_operators, filter_values)

    primary_field, secondary_field, *_ = selected_fields
    # Check axes labels
    if selected_axes == [Text.Y_AXIS, Text.X_AXIS]:
        axes = dict(y_axis=primary_field, x_axis=secondary_field)
    elif selected_axes == [Text.X_AXIS, Text.Y_AXIS]:
        axes = dict(x_axis=primary_field, y_axis=secondary_field)
    else:
        raise ValueError("Invalid axes")

    tab = Tab(ctx.triggered_id["tab"])
    return PlotBuilder(df).plot(
        fields=selected_fields,
        plot_type=tab.plot_type,
        **axes,
    )


def reset_filters(n_clicks):
    if n_clicks is None:
        return

    filter_operators, filter_values = ctx.outputs_grouping
    # Set default operators and reset values to None
    return [
        Filter(operator["id"]["filter"]).default_operator
        for operator in filter_operators
    ], [None for _ in filter_values]


def register_callbacks(app):
    match_fields = {"type": Page.FIELD_DROPDOWN, "tab": MATCH, "index": ALL}
    match_axes = {"type": Page.AXIS_TEXT, "tab": MATCH, "index": ALL}
    match_filter_operators = {
        "type": Page.FILTER_OPERATOR,
        "tab": MATCH,
        "filter": ALL,
        "index": ALL,
    }
    match_filter_values = {
        "type": Page.FILTER_VALUE,
        "tab": MATCH,
        "filter": ALL,
        "index": ALL,
    }
    match_swap_axes = {"type": Page.SWAP_AXES_BUTTON, "tab": MATCH}
    match_update_graph = {"type": Page.UPDATE_GRAPH_BUTTON, "tab": MATCH}
    match_reset_filter = {"type": Page.RESET_FILTER_BUTTON, "tab": MATCH}

    app.callback(
        Output(match_fields, "data"),
        Input(match_fields, "value"),
        State(match_fields, "data"),
    )(update_dropdown_options)
    app.callback(
        Output(match_axes, "children"),
        Input(match_swap_axes, "n_clicks"),
        State(match_axes, "children"),
    )(swap_axes)
    app.callback(
        Output({"type": Page.GRAPH, "tab": MATCH}, "figure"),
        inputs=dict(
            n_clicks=Input(match_update_graph, "n_clicks"),
            selected_fields=State(match_fields, "value"),
            selected_axes=State(match_axes, "children"),
            filter_operators=State(
                match_filter_operators,
                "value",
            ),
            filter_values=State(
                match_filter_values,
                "value",
            ),
        ),
    )(render_graph)
    app.callback(
        Output(
            match_filter_operators,
            "value",
        ),
        Output(
            match_filter_values,
            "value",
        ),
        Input(match_reset_filter, "n_clicks"),
    )(reset_filters)