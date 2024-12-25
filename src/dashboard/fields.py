import dash_mantine_components as dmc
from dash_iconify import DashIconify

from enums import Page, Tab, Text, Field

FIELD_SPAN = 3
AGGREGATION_SPAN = 1.5


def get_aggregation_info(field: Field):
    data = Field(field).aggregations if field else []
    value = data[0] if data else None
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

        # TODO: If has extra aggregations in 3 variables, drop span to 2
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
