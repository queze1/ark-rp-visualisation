import dash_mantine_components as dmc
from dash import dcc
from dash_iconify import DashIconify

from enums import Page, Tab
from frontend.filters import filter_controls


def make_tab(tab: Tab):
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
                size="sm",
                ta="center",
            ),
            span=3,
        )

    # Approximately same width as "By"
    swap_axis_button = dmc.Button(
        id={"type": Page.SWAP_AXIS_BUTTON, "tab": tab},
        children=DashIconify(icon="bi:arrow-left-right", width=18),
        variant="subtle",
        color="none",
        style={"padding": 8},
    )

    field_controls = dmc.Stack(
        [
            dmc.Grid(
                [
                    make_field_text("Plot"),
                    make_field(tab.primary_field, index=0),
                    make_field_text("By"),
                    make_field(tab.secondary_field, index=1),
                ],
                justify="center",
            ),
            dmc.Grid(
                [
                    make_field_text("Plot", hidden=True),
                    make_axis_text("Y-Axis", index=0),
                    swap_axis_button,
                    make_axis_text("X-Axis", index=1),
                ],
                justify="center",
                align="center",
            ),
        ],
        gap=5,
    )

    return dmc.Card(
        [
            field_controls,
            dmc.Divider(my=25),
            filter_controls,
            dmc.Space(h=20),
            dmc.Button(
                "This is how I like it!",
                ml="auto",
                maw=200,
                id={"type": Page.SUBMIT_BUTTON, "tab": tab},
            ),
            dmc.Space(h=20),
            dcc.Graph(
                id={"type": Page.GRAPH, "tab": tab},
            ),
        ],
        withBorder=True,
    )
