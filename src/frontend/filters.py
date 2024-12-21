import dash_mantine_components as dmc
from enums import Operator
from dash import html


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
