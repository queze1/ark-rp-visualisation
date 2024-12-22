import dash_mantine_components as dmc
from enums import Filter, FilterOption, Tab, Page
from dash import html
from data_loader import df

from functools import lru_cache


@lru_cache()
def get_unique(field):
    return sorted(df[field].unique())


def make_filter_controls(tab: Tab):
    def make_filter_group(filter: Filter, index):
        select_kwargs = filter.select_kwargs
        # Check if options need to be loaded dynamically
        if select_kwargs.get("data") == FilterOption.FIELD_UNIQUE:
            select_kwargs["data"] = get_unique(filter)

        return dmc.Group(
            [
                html.Label(filter.label),
                dmc.Select(
                    id={
                        "type": Page.FILTER_OPERATOR,
                        "tab": tab,
                        "filter": filter,
                        "index": index,
                    },
                    data=filter.operators,
                    value=filter.default_operator,
                ),
                filter.select_component(
                    id={
                        "type": Page.FILTER_VALUE,
                        "tab": tab,
                        "filter": filter,
                        "index": index,
                    },
                    **select_kwargs,
                ),
            ],
            grow=1,
        )

    header = dmc.Group(
        [
            dmc.Text("Filters", size="lg"),
            dmc.Button(
                id={"type": Page.FILTER_RESET, "tab": tab},
                children=dmc.Text("Reset", size="sm"),
                variant="subtle",
                color="black",
            ),
        ],
        justify="space-between",
        align="center",
        mb=10,
    )

    filter_groups = [
        make_filter_group(filter, index=i) for i, filter in enumerate(Filter)
    ]

    return dmc.Stack([header] + filter_groups, gap=5)
