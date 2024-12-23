from dashboard.filters import make_default_filters, make_filter_group, make_filter_value
from enums import Field, Filter, Page, Text, Tab, Operator, Plot

from dash import ALL, Input, Output, State, MATCH, Patch, ctx
from data_loader import df
from dashboard.plot_builder import PlotBuilder


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

            return is_duplicate or is_invalid_temporal

        patched_options = Patch()
        for i, opt in enumerate(options):
            patched_options[i]["disabled"] = process_option(opt)
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
    filters,
):
    if n_clicks is None or not all(selected_fields):
        return {}

    selected_fields = [Field(field) for field in selected_fields]
    primary_field, secondary_field, *_ = selected_fields
    # Find field axes
    if selected_axes == [Text.Y_AXIS, Text.X_AXIS]:
        axes = dict(y_axis=primary_field, x_axis=secondary_field)
    elif selected_axes == [Text.X_AXIS, Text.Y_AXIS]:
        axes = dict(x_axis=primary_field, y_axis=secondary_field)
    else:
        raise ValueError("Invalid axes")

    # Process filters
    filters = [
        (Filter(filter), Operator(operator), Filter(filter).post_processing(value))
        for filter, operator, value in zip(*filters)
        if value
    ]

    tab = Tab(ctx.triggered_id["tab"])
    return PlotBuilder(df).plot(
        fields=selected_fields,
        plot_type=Plot(tab.plot_type),
        filters=filters,
        **axes,
    )


def reset_filters(n_clicks):
    if n_clicks is None:
        return

    tab = Tab(ctx.triggered_id["tab"])
    # Recreate default filters
    return make_default_filters(tab)


def add_filter(n_clicks):
    if n_clicks is None:
        return

    tab = Tab(ctx.triggered_id["tab"])
    patched_children = Patch()
    patched_children.append(make_filter_group(tab, Filter.DATE))
    return patched_children


# Updates the filter operators and value input when the filter type changes
def update_filter_options(filter_type):
    filter_type = Filter(filter_type)

    c = ctx.triggered_id
    tab, index = c["tab"], c["index"]
    return (
        filter_type.operators,
        filter_type.default_operator,
        make_filter_value(filter_type, tab, index),
    )


def delete_filter(n_clicks, children):
    patched_children = Patch()
    # Adding a new filter triggers this for some reason, ignore if no clicks
    if not any(n_clicks):
        return patched_children

    # Find the filter group with same index and get its position in children
    index = ctx.triggered_id["index"]
    (filter_index,) = [
        i for i, child in enumerate(children) if child["props"]["id"]["index"] == index
    ]

    # Delete that filter group
    del patched_children[filter_index]
    return patched_children


def register_callbacks(app):
    match_fields = {"type": Page.FIELD_DROPDOWN, "tab": MATCH, "index": ALL}
    app.callback(
        Output(match_fields, "data"),
        Input(match_fields, "value"),
        State(match_fields, "data"),
    )(update_dropdown_options)

    match_axes = {"type": Page.AXIS_TEXT, "tab": MATCH, "index": ALL}
    match_swap_axes = {"type": Page.SWAP_AXES_BUTTON, "tab": MATCH}
    app.callback(
        Output(match_axes, "children"),
        Input(match_swap_axes, "n_clicks"),
        State(match_axes, "children"),
    )(swap_axes)

    match_update_graph = {"type": Page.UPDATE_GRAPH_BUTTON, "tab": MATCH}
    match_filter_types = {
        "type": Page.FILTER_TYPE,
        "tab": MATCH,
        "index": ALL,
    }
    match_filter_operators = {
        "type": Page.FILTER_OPERATOR,
        "tab": MATCH,
        "index": ALL,
    }
    match_filter_values = {
        "type": Page.FILTER_VALUE,
        "tab": MATCH,
        "index": ALL,
    }
    app.callback(
        Output({"type": Page.GRAPH, "tab": MATCH}, "figure"),
        inputs=dict(
            n_clicks=Input(match_update_graph, "n_clicks"),
            selected_fields=State(match_fields, "value"),
            selected_axes=State(match_axes, "children"),
            filters=(
                State(
                    match_filter_types,
                    "value",
                ),
                State(
                    match_filter_operators,
                    "value",
                ),
                State(
                    match_filter_values,
                    "value",
                ),
            ),
        ),
    )(render_graph)

    match_filter_container = {"type": Page.FILTER_CONTAINER, "tab": MATCH}
    match_reset_filter = {"type": Page.RESET_FILTER_BUTTON, "tab": MATCH}
    match_add_filter = {"type": Page.ADD_FILTER_BUTTON, "tab": MATCH}
    app.callback(
        Output(match_filter_container, "children", allow_duplicate=True),
        Input(match_reset_filter, "n_clicks"),
    )(reset_filters)
    app.callback(
        Output(match_filter_container, "children", allow_duplicate=True),
        Input(match_add_filter, "n_clicks"),
    )(add_filter)

    # Matches single elements within a filter group
    match_filter_operator = {
        "type": Page.FILTER_OPERATOR,
        "tab": MATCH,
        "index": MATCH,
    }
    match_filter_value_container = {
        "type": Page.FILTER_VALUE_CONTAINER,
        "tab": MATCH,
        "index": MATCH,
    }
    match_filter_type = {
        "type": Page.FILTER_TYPE,
        "tab": MATCH,
        "index": MATCH,
    }
    app.callback(
        Output(
            match_filter_operator,
            "data",
        ),
        Output(
            match_filter_operator,
            "value",
        ),
        Output(
            match_filter_value_container,
            "children",
        ),
        Input(
            match_filter_type,
            "value",
        ),
    )(update_filter_options)

    match_delete_filter = {
        "type": Page.DELETE_FILTER_BUTTON,
        "tab": MATCH,
        "index": ALL,
    }
    app.callback(
        Output(match_filter_container, "children", allow_duplicate=True),
        Input(match_delete_filter, "n_clicks"),
        State(match_filter_container, "children"),
    )(delete_filter)
