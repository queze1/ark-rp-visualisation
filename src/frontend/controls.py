from enums import Field, Operator, Tab
from dash import html
import dash_mantine_components as dmc


def make_controls(tab: Tab):
    def make_field_text(text):
        return dmc.GridCol(dmc.Text(text, size="lg"), span="content")

    def make_field_dropdown(index, condition=lambda _: True, **kwargs):
        return dmc.Select(
            id={"type": f"{tab}-field-dropdown", "index": index},
            data=[
                {"label": field.label, "value": field}
                for field in Field
                if field.label and condition(field)
            ],
            **kwargs,
        )

    def make_field(label, field, index):
        return dmc.GridCol(
            dmc.Stack(
                [
                    make_field_dropdown(index=index, **field),
                    dmc.Text(label, size="sm"),
                ],
                align="center",
                gap=5,
            ),
            span=3,
        )

    def make_field_controls():
        field1, field2 = tab.fields
        return dmc.Grid(
            [
                make_field_text("Plot"),
                make_field("Y-Axis", field1, index=0),
                make_field_text("By"),
                make_field("X-Axis", field2, index=1),
            ],
            justify="center",
        )

    def make_filter_controls():
        return dmc.Stack(
            [
                dmc.Group(
                    [
                        dmc.Text("Filters", size="lg"),
                        dmc.Text("Reset"),
                    ],
                    justify="space-between",
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
            gap=2,
        )

    return dmc.Card(
        [
            make_field_controls(),
            dmc.Divider(my=25),
            make_filter_controls(),
        ],
        withBorder=True,
    )
