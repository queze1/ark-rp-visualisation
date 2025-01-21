from dash import ALL, MATCH, Input, Output, Patch, State, ctx

from dashboard.fields import get_aggregation_info
from dashboard.filters import make_default_filters, make_filter_group, make_filter_value
from dashboard.plot_builder import AxisConfig, FigureConfig, FilterConfig, PlotBuilder
from enums import Field, Filter, Page, Plot, Tab
from logging_setup import get_logger

logger = get_logger(__name__)


def update_dropdown(selected_fields, current_options, aggregate_displays):
    c = ctx.outputs_grouping

    # Check if any temporal field is already selected
    has_selected_temporal = any(
        [Field(field).temporal if field else None for field in selected_fields]
    )

    def process_options(selected_field, options):
        """
        Rules for dropdown options:
        1. No duplicate options.
        2. No more than one temporal field.

        """

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

    def process_aggregates():
        agg_change = 0

        triggered_index = ctx.triggered_id["index"]
        # Get the list of aggregate outputs
        aggs = c["aggregates"]["value"]
        # Generate an empty patch for every agg output
        patched_aggregates = dict(
            display=[Patch() for _ in aggs],
            spacing_display=[Patch() for _ in aggs],
            option=[Patch() for _ in aggs],
            value=[Patch() for _ in aggs],
        )

        # Update the agg of the changed dropdown if it has one
        if triggered_index < len(aggs):
            field = selected_fields[triggered_index]
            agg_info = get_aggregation_info(field)
            patched_aggregates["display"][triggered_index] = agg_info["display"]
            patched_aggregates["spacing_display"][triggered_index] = agg_info["display"]
            patched_aggregates["option"][triggered_index] = agg_info["data"]
            patched_aggregates["value"][triggered_index] = agg_info["value"]

            # Calculate the change in aggs
            agg_change += (agg_info["display"] == "block") - (
                aggregate_displays[triggered_index] == "block"
            )

        return patched_aggregates, agg_change

    def process_spans(agg_change):
        patched_spans = dict(
            field=[Patch() for _ in c["spans"]["field"]],
            spacing=[Patch() for _ in c["spans"]["spacing"]],
        )

        # Skip if not 3 variables
        if len(selected_fields) != 3:
            return patched_spans

        # Check if there is at least one aggregate displayed
        current_aggs = (
            sum([display == "block" for display in aggregate_displays]) + agg_change
        )
        # Set to 3 if no aggs
        if current_aggs == 0:
            return dict(
                field=[3 for _ in c["spans"]["field"]],
                spacing=[3 for _ in c["spans"]["spacing"]],
            )
        else:
            # If aggs, reduce to 2
            return dict(
                field=[2 for _ in c["spans"]["field"]],
                spacing=[2 for _ in c["spans"]["spacing"]],
            )

    # Generate a patch for every field
    patched_field_options = [
        process_options(selected_field, options)
        for selected_field, options in zip(selected_fields, current_options)
    ]
    patched_aggregates, agg_change = process_aggregates()
    patched_spans = process_spans(agg_change)
    return dict(
        field_options=patched_field_options,
        aggregates=patched_aggregates,
        spans=patched_spans,
    )


def swap_axes(n_clicks, axes):
    if n_clicks is None:
        return axes

    left, right = axes
    return [right, left]


def render_graph(
    n_clicks,
    selected_fields,
    selected_axes,
    selected_aggregations,
    filters,
    customisation,
):
    if n_clicks is None or not all(selected_fields):
        return {}

    tab = Tab(ctx.triggered_id["tab"])

    # Log graph creation
    summary = f"""
    User created a graph:
        Plot Type: {tab.label}
        {selected_axes[0]}: ({selected_fields[0]})
        {selected_axes[1]}: ({selected_fields[1]})
        Aggregations: {selected_aggregations}
        Filters: {filters}
        Customizations: {customisation}
    """
    logger.info(summary.strip())

    return PlotBuilder(
        plot_type=Plot(tab.plot_type),
        axis_config=AxisConfig.from_raw(
            selected_fields=selected_fields,
            selected_axes=selected_axes,
            selected_aggregations=selected_aggregations,
        ),
        filter_config=FilterConfig.from_raw(filters=filters),
        figure_config=FigureConfig.from_raw(**customisation),
    ).build()


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


def reset_customisation(n_clicks):
    if n_clicks is None:
        return

    # Set all options to empty
    return dict(
        title="",
        x_label="",
        y_label="",
        moving_averages={
            7: False,
            30: False,
        },
        sort_order=None,
        sort_axis=None,
        x_log="",
        y_log="",
    )


def register_callbacks(app):
    match_fields = {"type": Page.FIELD_DROPDOWN, "tab": MATCH, "index": ALL}
    match_agg_containers = {
        "type": Page.FIELD_AGG_CONTAINER,
        "tab": MATCH,
        "index": ALL,
    }
    match_agg_spacings = {"type": Page.FIELD_AGG_SPACING, "tab": MATCH, "index": ALL}
    match_agg_dropdowns = {"type": Page.FIELD_AGG_DROPDOWN, "tab": MATCH, "index": ALL}
    match_field_containers = {
        "type": Page.FIELD_AGG_CONTAINER,
        "tab": MATCH,
        "index": ALL,
    }
    app.callback(
        output=dict(
            field_options=Output(match_fields, "data"),
            aggregates=dict(
                display=Output(
                    match_agg_containers,
                    "display",
                ),
                spacing_display=Output(
                    match_agg_spacings,
                    "display",
                ),
                option=Output(
                    match_agg_dropdowns,
                    "data",
                ),
                value=Output(
                    match_agg_dropdowns,
                    "value",
                ),
            ),
            spans=dict(
                field=Output(
                    {"type": Page.FIELD_CONTAINER, "tab": MATCH, "index": ALL}, "span"
                ),
                spacing=Output(
                    {"type": Page.FIELD_SPACING, "tab": MATCH, "index": ALL}, "span"
                ),
            ),
        ),
        inputs=[
            Input(match_fields, "value"),
            State(match_fields, "data"),
            State(match_field_containers, "display"),
        ],
        prevent_initial_call=True,
    )(update_dropdown)

    match_axes = {"type": Page.AXIS_TEXT, "tab": MATCH, "index": ALL}
    match_swap_axes = {"type": Page.SWAP_AXES_BUTTON, "tab": MATCH}
    app.callback(
        Output(match_axes, "children"),
        Input(match_swap_axes, "n_clicks"),
        State(match_axes, "children"),
        prevent_initial_call=True,
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
    match_title_input = {"type": Page.TITLE_INPUT, "tab": MATCH}
    match_x_label = {"type": Page.X_LABEL_INPUT, "tab": MATCH}
    match_y_label = {"type": Page.Y_LABEL_INPUT, "tab": MATCH}
    match_mavg_7 = {"type": Page.MOVING_AVERAGE_7, "tab": MATCH}
    match_mavg_30 = {"type": Page.MOVING_AVERAGE_30, "tab": MATCH}
    match_sort_order = {"type": Page.SORT_ORDER_DROPDOWN, "tab": MATCH}
    match_sort_axis = {"type": Page.SORT_AXIS_DROPDOWN, "tab": MATCH}
    match_x_log = {"type": Page.X_LOG_CHECKBOX, "tab": MATCH}
    match_y_log = {"type": Page.Y_LOG_CHECKBOX, "tab": MATCH}
    app.callback(
        Output({"type": Page.GRAPH, "tab": MATCH}, "figure"),
        inputs=dict(
            n_clicks=Input(match_update_graph, "n_clicks"),
            selected_fields=State(match_fields, "value"),
            selected_axes=State(match_axes, "children"),
            selected_aggregations=State(
                match_agg_dropdowns,
                "value",
            ),
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
            customisation=dict(
                title=State(match_title_input, "value"),
                x_label=State(match_x_label, "value"),
                y_label=State(match_y_label, "value"),
                moving_averages={
                    7: State(match_mavg_7, "checked"),
                    30: State(match_mavg_30, "checked"),
                },
                sort_order=State(match_sort_order, "value"),
                sort_axis=State(match_sort_axis, "value"),
                x_log=State(match_x_log, "checked"),
                y_log=State(match_y_log, "checked"),
            ),
        ),
        prevent_initial_call=True,
    )(render_graph)

    match_filter_container = {"type": Page.FILTER_CONTAINER, "tab": MATCH}
    match_reset_filter = {"type": Page.RESET_FILTER_BUTTON, "tab": MATCH}
    match_add_filter = {"type": Page.ADD_FILTER_BUTTON, "tab": MATCH}
    app.callback(
        Output(match_filter_container, "children", allow_duplicate=True),
        Input(match_reset_filter, "n_clicks"),
        prevent_initial_call=True,
    )(reset_filters)
    app.callback(
        Output(match_filter_container, "children", allow_duplicate=True),
        Input(match_add_filter, "n_clicks"),
        prevent_initial_call=True,
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
        prevent_initial_call=True,
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
        prevent_initial_call=True,
    )(delete_filter)

    match_reset_customisation = {"type": Page.RESET_CUSTOMISATION_BUTTON, "tab": MATCH}
    app.callback(
        output=dict(
            title=Output(match_title_input, "value"),
            x_label=Output(match_x_label, "value"),
            y_label=Output(match_y_label, "value"),
            moving_averages={
                7: Output(match_mavg_7, "checked"),
                30: Output(match_mavg_30, "checked"),
            },
            sort_order=Output(match_sort_order, "value"),
            sort_axis=Output(match_sort_axis, "value"),
            x_log=Output(match_x_log, "checked"),
            y_log=Output(match_y_log, "checked"),
        ),
        inputs=Input(match_reset_customisation, "n_clicks"),
        prevent_initial_call=True,
    )(reset_customisation)
