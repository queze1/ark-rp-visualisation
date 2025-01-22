import dash_mantine_components as dmc
from dash import Input, Output, Patch, State, ctx
from dash_iconify import DashIconify

from dashboard.callback_patterns import (
    match_agg_containers,
    match_agg_dropdowns,
    match_agg_spacings,
    match_axes,
    match_field_containers,
    match_fields,
    match_swap_axes,
    match_field_spacings,
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
    # Default aggregation is first one in the list
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
        aggregation_dropdown = dmc.Select(
            id={"type": Page.FIELD_AGG_DROPDOWN, "tab": tab, "index": index},
            data=aggregation_info["data"],
            value=aggregation_info["value"],
            allowDeselect=False,
        )

        field_dropdown = dmc.Select(
            id={"type": Page.FIELD_DROPDOWN, "tab": tab, "index": index},
            data=[
                {"label": field.label, "value": field}
                for field in field_options["allowed"]
            ],
            value=default_field,
        )

        # Don't render dropdown if not being grouped by
        components = [
            (
                dmc.GridCol(
                    aggregation_dropdown,
                    id={
                        "type": Page.FIELD_AGG_CONTAINER,
                        "tab": tab,
                        "index": index,
                    },
                    display=aggregation_info["display"],
                    span=AGGREGATION_SPAN,
                )
            )
            if grouped_by
            else None,
            dmc.GridCol(
                field_dropdown,
                id={"type": Page.FIELD_CONTAINER, "tab": tab, "index": index},
                span=FIELD_SPAN,
            ),
        ]

        return [component for component in components if component]

    def make_aggregation_spacing(field: Field, index):
        return dmc.GridCol(
            id={"type": Page.FIELD_AGG_SPACING, "tab": tab, "index": index},
            display=get_aggregation_info(field)["display"],
            span=AGGREGATION_SPAN,
        )

    def make_axis_text(index):
        # Only render text for X and Y axes
        text = [Text.Y_AXIS, Text.X_AXIS, None][index]
        return dmc.GridCol(
            dmc.Text(
                text,
                id={"type": Page.AXIS_TEXT, "tab": tab, "index": index},
                size="md",
                ta="center",
            )
            if text
            else None,
            id={"type": Page.FIELD_SPACING, "tab": tab, "index": index},
            # Same length as dropdown
            span=FIELD_SPAN,
        )

    swap_axes_button = dmc.Button(
        id={"type": Page.SWAP_AXES_BUTTON, "tab": tab},
        children=DashIconify(icon="bi:arrow-left-right", width=18),
        variant="subtle",
        color="none",
    )

    if len(tab.fields) == 2:
        top_separators = [Text.BY]
        swap_axes_button.px = 8
    elif len(tab.fields) == 3:
        top_separators = [Text.AND, Text.BY]
        swap_axes_button.px = 15

    # Start with "Plot" text and hidden "Plot" text for spacing
    top_components = [make_field_text(Text.PLOT)]
    bottom_components = [make_field_text(Text.PLOT, hidden=True)]

    for i, field in enumerate(tab.fields):
        # Group by all fields except the last one
        grouped_by = i < len(tab.fields) - 1
        # Add dropdowns to top components
        top_components.extend(
            make_field_dropdowns(field, index=i, grouped_by=grouped_by)
        )

        # Add spacing and axis text to bottom components
        if grouped_by:
            bottom_components.append(
                make_aggregation_spacing(field.get("default"), index=i)
            )
        bottom_components.append(
            make_axis_text(index=i),
        )

        if i < len(top_separators):
            # Add separator text to top components (e.g. "by" or "and")
            top_components.append(make_field_text(top_separators[i]))
            # Add swap axes button or hidden text for spacing to bottom components
            if i == 0:
                bottom_components.append(swap_axes_button)
            else:
                bottom_components.append(
                    make_field_text(top_separators[i], hidden=True)
                )

    return dmc.Stack(
        [
            dmc.Grid(
                top_components,
                justify="center",
                align="center",
            ),
            dmc.Grid(
                bottom_components,
                justify="center",
                align="center",
            ),
        ],
        gap=7,
    )


def register_field_callbacks(app):
    def update_dropdown(selected_fields, current_options):
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
            # print(f"c['aggregates'] {c['aggregates']}")
            # print(f"len {[len(_) for _ in c['aggregates'].values()]}")

            # Get the list of aggregate outputs
            aggs = c["aggregates"]["value"]
            # Generate an empty patch for every agg output
            patched_aggregates = dict(
                display=[Patch() for _ in aggs],
                spacing_display=[Patch() for _ in aggs],
                option=[Patch() for _ in aggs],
                value=[Patch() for _ in aggs],
            )

            triggered_index = ctx.triggered_id["index"]
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

            return patched_aggregates

        def process_spans():
            patched_spans = dict(
                field=[Patch() for _ in c["spans"]["field"]],
                spacing=[Patch() for _ in c["spans"]["spacing"]],
            )

            # Skip if not 3 variables
            if len(selected_fields) != 3:
                return patched_spans

            # Check if there is at least one aggregate displayed
            num_aggs = sum(
                [
                    get_aggregation_info(field)["display"] == "block"
                    for field in selected_fields
                ]
            )

            # Set to 3 if no aggs
            if num_aggs == 0:
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
        return dict(
            field_options=patched_field_options,
            aggregates=process_aggregates(),
            spans=process_spans(),
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
                field=Output(match_field_containers, "span"),
                spacing=Output(match_field_spacings, "span"),
            ),
        ),
        inputs=[
            Input(match_fields, "value"),
            State(match_fields, "data"),
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
