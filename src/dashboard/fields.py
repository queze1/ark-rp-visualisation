import dash_mantine_components as dmc
from dash import ALL, MATCH, Input, Output, Patch, State, ctx
from dash_iconify import DashIconify

from dashboard.callback_patterns import (
    match_agg_containers,
    match_agg_dropdowns,
    match_agg_spacings,
    match_axes,
    match_field_containers,
    match_fields,
    match_swap_axes,
)
from enums import Field, GroupBy, Page, Tab, Text

FIELD_SPAN = 3
AGGREGATION_SPAN = 1.5


def get_aggregation_info(field: Field):
    data = (
        [
            {"label": GroupBy(agg).label, "value": GroupBy(agg)}
            for agg in Field(field).aggregations
        ]
        if field
        else []
    )
    value = data[0]["value"] if data else None
    display = "block" if len(data) > 1 else "none"
    return dict(data=data, value=value, display=display)


def make_field_controls(tab: Tab):
    def make_field_text(text, hidden=False):
        style = {"visibility": "hidden"} if hidden else {}
        return dmc.GridCol(dmc.Text(text, size="lg", style=style), span="content")

    def make_field_dropdowns(field_options, index, grouped_by=False):
        default_field = field_options.get("default")
        aggregation_info = get_aggregation_info(default_field)
        # Don't render dropdown if not being grouped by
        aggregation_dropdown = (
            dmc.Select(
                id={"type": Page.FIELD_AGG_DROPDOWN, "tab": tab, "index": index},
                data=aggregation_info["data"],
                value=aggregation_info["value"],
                allowDeselect=False,
            )
            if grouped_by
            else None
        )
        field_dropdown = dmc.Select(
            id={"type": Page.FIELD_DROPDOWN, "tab": tab, "index": index},
            data=[
                {"label": field.label, "value": field}
                for field in field_options["allowed"]
            ],
            value=default_field,
        )

        aggregation_col = (
            dmc.GridCol(
                aggregation_dropdown,
                id={"type": Page.FIELD_AGG_CONTAINER, "tab": tab, "index": index},
                # A field only has an aggregation dropdown shown if it has more than one possible option
                display=aggregation_info["display"],
                span=AGGREGATION_SPAN,
            )
            if grouped_by
            else None
        )

        field_col = dmc.GridCol(
            field_dropdown,
            id={"type": Page.FIELD_CONTAINER, "tab": tab, "index": index},
            span=FIELD_SPAN,
        )

        return ([aggregation_col] if aggregation_col else []) + [field_col]

    def make_aggregation_spacing(field: Field, index):
        return dmc.GridCol(
            id={"type": Page.FIELD_AGG_SPACING, "tab": tab, "index": index},
            display=get_aggregation_info(field)["display"],
            span=AGGREGATION_SPAN,
        )

    def make_axis_text(text, index):
        # Same length as dropdown, to be centred under them
        return dmc.GridCol(
            dmc.Text(
                text,
                id={"type": Page.AXIS_TEXT, "tab": tab, "index": index},
                size="md",
                ta="center",
            ),
            id={"type": Page.FIELD_SPACING, "tab": tab, "index": index},
            span=FIELD_SPAN,
        )

    if not tab.tertiary_field:
        primary_dropdowns, secondary_dropdowns, tertiary_dropdowns = (
            make_field_dropdowns(tab.primary_field, index=0, grouped_by=True),
            make_field_dropdowns(tab.secondary_field, index=1),
            None,
        )

        # Two variables
        dropdowns = primary_dropdowns + [make_field_text(Text.BY)] + secondary_dropdowns
    else:
        primary_dropdowns, secondary_dropdowns, tertiary_dropdowns = (
            make_field_dropdowns(tab.primary_field, index=0, grouped_by=True),
            make_field_dropdowns(tab.secondary_field, index=1, grouped_by=True),
            make_field_dropdowns(tab.tertiary_field, index=2),
        )

        # Three variables
        dropdowns = (
            primary_dropdowns
            + [make_field_text(Text.AND)]
            + secondary_dropdowns
            + [make_field_text(Text.BY)]
            + tertiary_dropdowns
        )

    # Manually add paddingX to match the width of its above div
    swap_axes_button = dmc.Button(
        id={"type": Page.SWAP_AXES_BUTTON, "tab": tab},
        children=DashIconify(icon="bi:arrow-left-right", width=18),
        variant="subtle",
        color="none",
        px=(15 if tab.tertiary_field else 8),
    )

    top_row = dmc.Grid(
        [
            make_field_text(Text.PLOT),
        ]
        + dropdowns,
        justify="center",
        align="center",
    )

    if not tab.tertiary_field:
        bottom_row_components = [
            make_field_text(Text.PLOT, hidden=True),
            make_aggregation_spacing(tab.primary_field.get("default"), index=0),
            make_axis_text(Text.Y_AXIS, index=0),
            swap_axes_button,
            make_axis_text(Text.X_AXIS, index=1),
        ]
    else:
        # Extra space if 3 variables
        bottom_row_components = [
            make_field_text(Text.PLOT, hidden=True),
            make_aggregation_spacing(tab.primary_field.get("default"), index=0),
            make_axis_text(Text.Y_AXIS, index=0),
            swap_axes_button,
            make_aggregation_spacing(tab.secondary_field.get("default"), index=1),
            make_axis_text(Text.X_AXIS, index=1),
            make_field_text(Text.BY, hidden=True),
            dmc.GridCol(
                id={"type": Page.FIELD_SPACING, "tab": tab, "index": 2}, span=3
            ),
        ]

    bottom_row = dmc.Grid(
        bottom_row_components,
        justify="center",
        align="center",
    )

    return dmc.Stack(
        [
            top_row,
            bottom_row,
        ],
        gap=7,
    )


def register_field_callbacks(app):
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
                patched_aggregates["spacing_display"][triggered_index] = agg_info[
                    "display"
                ]
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
    )(update_dropdown)

    def swap_axes(n_clicks, axes):
        if n_clicks is None:
            return axes

        left, right = axes
        return [right, left]

    app.callback(
        Output(match_axes, "children"),
        Input(match_swap_axes, "n_clicks"),
        State(match_axes, "children"),
    )(swap_axes)
