import dash_mantine_components as dmc
from dash_iconify import DashIconify

from enums import Page, Tab, Text


def make_field_controls(tab: Tab):
    def make_field_text(text, hidden=False):
        style = {"visibility": "hidden"} if hidden else {}
        return dmc.GridCol(dmc.Text(text, size="lg", style=style), span="content")

    def make_field(field_options, index):
        dropdown = dmc.Select(
            id={"type": Page.FIELD_DROPDOWN, "tab": tab, "index": index},
            data=[
                {"label": field.label, "value": field}
                for field in field_options["allowed"]
            ],
            value=field_options.get("default"),
        )

        return dmc.GridCol(
            dropdown,
            span=3,
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
        # Two variables
        dropdowns = [
            make_field(tab.primary_field, index=0),
            make_field_text(Text.BY),
            make_field(tab.secondary_field, index=1),
        ]
    else:
        # Three variables
        dropdowns = [
            make_field(tab.primary_field, index=0),
            make_field_text(Text.AND),
            make_field(tab.secondary_field, index=1),
            make_field_text(Text.BY),
            make_field(tab.tertiary_field, index=2),
        ]

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
