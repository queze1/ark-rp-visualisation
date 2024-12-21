import dash_mantine_components as dmc
from dash import dcc, html

from enums import Operator, Page, Tab


def make_tab(tab: Tab):
    def make_field_text(text):
        return dmc.GridCol(dmc.Text(text, size="lg"), span="content")

    def make_field(label, field_options, index):
        dropdown = dmc.Select(
            id={"type": Page.FIELD_DROPDOWN(tab), "index": index},
            data=[
                {"label": field.label, "value": field}
                for field in field_options["allowed"]
            ],
            value=field_options.get("default"),
        )

        return dmc.GridCol(
            dmc.Stack(
                [
                    dropdown,
                    dmc.Text(label, size="sm"),
                ],
                align="center",
                gap=5,
            ),
            span=3,
        )

    field_controls = dmc.Grid(
        [
            make_field_text("Plot"),
            make_field("Y-Axis", tab.primary_field, index=0),
            make_field_text("By"),
            make_field("X-Axis", tab.secondary_field, index=1),
        ],
        justify="center",
    )

    filter_controls = dmc.Stack(
        [
            dmc.Group(
                [
                    dmc.Text("Filters", size="lg"),
                    dmc.Button(
                        children=dmc.Text("Reset", size="sm"),
                        variant="subtle",
                        color="black",
                    ),
                ],
                justify="space-between",
                align="center",
                mb=10,
            ),
            dmc.Group(
                [
                    html.Label("Date"),
                    dmc.Select(
                        data=[Operator.BEFORE, Operator.DURING, Operator.AFTER],
                        value=Operator.DURING,
                    ),
                    dmc.DatePickerInput(),
                ],
                grow=1,
            ),
            dmc.Group(
                [
                    html.Label("User"),
                    dmc.Select(
                        data=[Operator.IS, Operator.IS_NOT],
                        value=Operator.IS,
                    ),
                    dmc.MultiSelect(
                        data=["New York City", "Montreal", "San Francisco"],
                        placeholder="Select...",
                    ),
                ],
                grow=1,
            ),
            dmc.Group(
                [
                    html.Label("Channel Name"),
                    dmc.Select(
                        data=[Operator.IS, Operator.IS_NOT],
                        value=Operator.IS,
                    ),
                    dmc.MultiSelect(
                        data=["New York City", "Montreal", "San Francisco"],
                        placeholder="Select...",
                    ),
                ],
                grow=1,
            ),
            dmc.Group(
                [
                    html.Label("Hour"),
                    dmc.Select(
                        data=[
                            Operator.LT,
                            Operator.LEQ,
                            Operator.GT,
                            Operator.GEQ,
                            Operator.EQ,
                        ],
                        value=Operator.GEQ,
                    ),
                    dmc.Select(
                        data=[str(hour) for hour in range(24)],
                        placeholder="Enter hour...",
                    ),
                ],
                grow=1,
            ),
            dmc.Group(
                [
                    html.Label("Reaction Count"),
                    dmc.Select(
                        data=[operator for operator in Operator], value=Operator.GEQ
                    ),
                    dmc.NumberInput(
                        min=0,
                        max=99,
                        allowDecimal=False,
                        placeholder="Enter number...",
                    ),
                ],
                grow=1,
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
                id=Page.UPDATE_GRAPH_BUTTON(tab),
            ),
            dcc.Graph(id=Page.GRAPH(tab)),
        ],
        withBorder=True,
    )
