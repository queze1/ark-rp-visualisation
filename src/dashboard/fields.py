import dash_mantine_components as dmc
from dash_iconify import DashIconify

from enums import Page, Tab, Text, Field


def make_field_controls(tab: Tab):
    def make_field_text(text, hidden=False):
        style = {"visibility": "hidden"} if hidden else {}
        return dmc.GridCol(dmc.Text(text, size="lg", style=style), span="content")

    def make_field_input(field_options, index):
        default_field = field_options.get("default")
        default_aggregations = (
            Field(default_field).aggregations if default_field else []
        )

        aggregation_dropdown = dmc.Select(
            id={"type": Page.FIELD_AGG_DROPDOWN, "tab": tab, "index": index},
            data=[groupby for groupby in default_aggregations],
            value=default_aggregations[0] if default_aggregations else None,
        )

        field_dropdown = dmc.Select(
            id={"type": Page.FIELD_DROPDOWN, "tab": tab, "index": index},
            data=[
                {"label": field.label, "value": field}
                for field in field_options["allowed"]
            ],
            value=default_field,
        )

        return [
            dmc.GridCol(
                aggregation_dropdown,
                display="block" if len(default_aggregations) > 1 else "none",
                span=1.5,
            ),
            dmc.GridCol(
                field_dropdown,
                span=3,
            ),
        ]

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
        # Two variables
        dropdowns = (
            make_field_input(tab.primary_field, index=0)
            + [make_field_text(Text.BY)]
            + make_field_input(tab.secondary_field, index=1)
        )
    else:
        # TODO: If has extra aggregations in 3 variables, drop span to 2
        # TODO: Add spacing depending on if aggregation dropdown is visible
        # Three variables
        dropdowns = (
            make_field_input(tab.primary_field, index=0)
            + [make_field_text(Text.AND)]
            + make_field_input(tab.secondary_field, index=1)
            + [make_field_text(Text.BY)]
            + make_field_input(tab.tertiary_field, index=2)
        )

    # Manually add paddingX to match the width of its above div
    swap_axes_button = dmc.Button(
        id={"type": Page.SWAP_AXES_BUTTON, "tab": tab},
        children=DashIconify(icon="bi:arrow-left-right", width=18),
        variant="subtle",
        color="none",
        px=(15 if tab.tertiary_field else 8),
    )

    return dmc.Stack(
        [
            dmc.Grid(
                [
                    make_field_text(Text.PLOT),
                ]
                + dropdowns,
                justify="center",
                align="center",
            ),
            dmc.Grid(
                [
                    make_field_text(Text.PLOT, hidden=True),
                    make_axis_text(Text.Y_AXIS, index=0),
                    swap_axes_button,
                    make_axis_text(Text.X_AXIS, index=1),
                ]
                # Insert extra space if three variables
                + (
                    [make_field_text(Text.BY, hidden=True), dmc.GridCol(span=3)]
                    if tab.tertiary_field
                    else []
                ),
                justify="center",
                align="center",
            ),
        ],
        gap=7,
    )
