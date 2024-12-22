import dash_mantine_components as dmc
from enums import Filter
from dash import html
from data_loader import df

from functools import lru_cache


@lru_cache()
def get_unique(field):
    return df[field].unique()


def make_filter_group(filter: Filter, value_select):
    return dmc.Group(
        [
            html.Label(filter.label),
            dmc.Select(
                data=filter.operators,
                value=filter.default_operator,
            ),
            value_select,
        ],
        grow=1,
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
        make_filter_group(
            Filter.DATE,
            dmc.DatePickerInput(),
        ),
        make_filter_group(
            Filter.AUTHOR,
            dmc.MultiSelect(
                data=get_unique(Filter.AUTHOR),
                placeholder="Select...",
            ),
        ),
        make_filter_group(
            Filter.CHANNEL_NAME,
            dmc.MultiSelect(
                data=get_unique(Filter.CHANNEL_NAME),
                placeholder="Select...",
            ),
        ),
        make_filter_group(
            Filter.HOUR,
            dmc.Select(
                data=[str(hour) for hour in range(24)],
                placeholder="Enter hour...",
            ),
        ),
        make_filter_group(
            Filter.REACTION_COUNT,
            dmc.NumberInput(
                min=0,
                max=99,
                allowDecimal=False,
                placeholder="Enter number...",
            ),
        ),
    ],
    gap=5,
)
