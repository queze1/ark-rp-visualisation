import dash_mantine_components as dmc
from dash import dcc
from dash_iconify import DashIconify

from enums import Page, Tab
from frontend.filters import filter_controls


def make_tab(tab: Tab):
    def make_field_text(text):
        return dmc.GridCol(dmc.Text(text, size="lg"), span="content")

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

    field_controls = dmc.Stack(
        [
            dmc.Grid(
                [
                    make_field_text("Plot"),
                    make_field("Y-Axis", tab.primary_field, index=0),
                    make_field_text("By"),
                    make_field("X-Axis", tab.secondary_field, index=1),
                ],
                justify="center",
            ),
            dmc.Grid(
                [
                    dmc.GridCol(
                        dmc.Text("Plot", size="lg"),
                        style={"visibility": "hidden"},
                        span="content",
                    ),
                    dmc.GridCol(
                        dmc.Text("Y-Axis", size="sm", ta="center"),
                        span=3,
                    ),
                    dmc.GridCol(DashIconify(icon="bi:arrow-repeat"), span="content"),
                    dmc.GridCol(
                        dmc.Text("X-Axis", size="sm", ta="center"),
                        span=3,
                    ),
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
