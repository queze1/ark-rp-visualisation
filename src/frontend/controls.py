from backend.enums import DateOperator, Field, MatchOperator, Operator
from dash import html
import dash_mantine_components as dmc
from dash import ALL, Input, Output, State


tab_field_controls = {
    "line": [
        {
            "condition": lambda field: not field.temporal,
        },
        {
            "value": Field.DATE,
            "condition": lambda field: field is Field.DATE,
        },
    ],
    "bar": [{"condition": lambda field: field is not Field.DATE}, {}],
    "scatter": [{}, {}],
}


def make_controls(tab):
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

    def make_field_controls(fields):
        field1, field2 = fields
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
                            data=[operator for operator in DateOperator],
                            value=DateOperator.BEFORE,
                        ),
                        dmc.DatePickerInput(),
                    ],
                    grow=1,
                ),
                dmc.Group(
                    [
                        html.Label("User"),
                        dmc.Select(
                            data=[operator for operator in MatchOperator],
                            value=MatchOperator.IS,
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
                            data=[operator for operator in MatchOperator],
                            value=MatchOperator.IS,
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
                            data=[operator for operator in Operator], value=Operator.GEQ
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
            make_field_controls(tab_field_controls[tab]),
            dmc.Divider(my=25),
            make_filter_controls(),
        ],
        withBorder=True,
    )


def register_controls_callbacks(app, tab):
    @app.callback(
        Output({"type": f"{tab}-field-dropdown", "index": ALL}, "data"),
        Input({"type": f"{tab}-field-dropdown", "index": ALL}, "value"),
        State({"type": f"{tab}-field-dropdown", "index": ALL}, "data"),
    )
    def update_dropdown_options(selected_fields, current_options):
        """
        Rules:
        1. No duplicate options.
        2. No more than one temporal field.
        """

        # Check if any temporal field is already selected
        has_selected_temporal = any(
            [Field(field).temporal if field else None for field in selected_fields]
        )

        def process_option(opt, dropdown_index):
            label, field = opt["label"], Field(opt["value"])

            # Check if field is already selected in another dropdown
            is_duplicate = (
                field in selected_fields and field != selected_fields[dropdown_index]
            )

            # Check if this dropdown has selected a temporal field
            selected_temporal = (
                Field(selected_fields[dropdown_index]).temporal
                if selected_fields[dropdown_index]
                else False
            )
            is_invalid_temporal = (
                field.temporal and has_selected_temporal and not selected_temporal
            )

            return {
                "label": label,
                "value": field,
                "disabled": is_duplicate or is_invalid_temporal,
            }

        return [
            [process_option(opt, i) for opt in options]
            for i, options in enumerate(current_options)
        ]
