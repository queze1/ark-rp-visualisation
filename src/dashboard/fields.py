import dash_mantine_components as dmc
from dash_iconify import DashIconify

from enums import Page, Tab, Text, Field


def make_field_controls(tab: Tab):
    def make_field_text(text, hidden=False):
        style = {"visibility": "hidden"} if hidden else {}
        return dmc.GridCol(dmc.Text(text, size="lg", style=style), span="content")

    def make_field_dropdowns(field_options, index, grouped_by=False):
        default_field = field_options.get("default")
        default_aggregations = (
            Field(default_field).aggregations if default_field else []
        )

        # Don't render dropdown if not being grouped by
        aggregation_dropdown = (
            dmc.Select(
                id={"type": Page.FIELD_AGG_DROPDOWN, "tab": tab, "index": index},
                data=default_aggregations,
                value=default_aggregations[0] if default_aggregations else None,
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
                display="block" if len(default_aggregations) > 1 else "none",
                span=1.5,
            )
            if grouped_by
            else None
        )

        field_col = dmc.GridCol(
            field_dropdown,
            span=3,
        )

        return dict(
            dropdowns=([aggregation_col] if aggregation_col else []) + [field_col],
            # Add extra space if aggregation dropdown is shown
            spacing_span=1.5 if grouped_by and len(default_aggregations) > 1 else 0,
        )

    def make_aggregation_spacing(span, index):
        return dmc.GridCol(
            [],
            id={"type": Page.FIELD_AGG_SPACING, "tab": tab, "index": index},
            span=span,
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
            span=3,
        )

    if not tab.tertiary_field:
        primary_components, secondary_components, tertiary_components = (
            make_field_dropdowns(tab.primary_field, index=0, grouped_by=True),
            make_field_dropdowns(tab.secondary_field, index=1),
            None,
        )

        # Two variables
        dropdowns = (
            primary_components["dropdowns"]
            + [make_field_text(Text.BY)]
            + secondary_components["dropdowns"]
        )
    else:
        primary_components, secondary_components, tertiary_components = (
            make_field_dropdowns(tab.primary_field, index=0, grouped_by=True),
            make_field_dropdowns(tab.secondary_field, index=1, grouped_by=True),
            make_field_dropdowns(tab.tertiary_field, index=2),
        )

        # TODO: If has extra aggregations in 3 variables, drop span to 2
        # Three variables
        dropdowns = (
            primary_components["dropdowns"]
            + [make_field_text(Text.AND)]
            + secondary_components["dropdowns"]
            + [make_field_text(Text.BY)]
            + tertiary_components["dropdowns"]
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

    bottom_row = dmc.Grid(
        [
            make_field_text(Text.PLOT, hidden=True),
            make_aggregation_spacing(span=primary_components["spacing_span"], index=0),
            make_axis_text(Text.Y_AXIS, index=0),
            swap_axes_button,
            make_aggregation_spacing(
                span=secondary_components["spacing_span"], index=0
            ),
            make_axis_text(Text.X_AXIS, index=1),
        ]
        # Insert extra space if three variables
        + (
            [
                make_field_text(Text.BY, hidden=True),
            ]
            if tertiary_components
            else []
        ),
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
