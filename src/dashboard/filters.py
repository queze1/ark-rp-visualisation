from uuid import uuid4
import dash_mantine_components as dmc
from enums import Filter, FilterOption, Tab, Page
from dash import html
from data_loader import df

from functools import lru_cache


@lru_cache()
def get_unique(field):
    return sorted(df[field].unique())


def make_filter_group(tab: Tab, filter: Filter):
    select_kwargs = filter.select_kwargs.copy()
    # Check if options need to be loaded dynamically
    if select_kwargs.get("data") == FilterOption.FIELD_UNIQUE:
        select_kwargs["data"] = get_unique(filter)

    # Use random index since filters can be created dynamically
    index = str(uuid4())
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
                allowDeselect=False,
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


def make_filter_controls(tab: Tab):
    header = dmc.Group(
        [
            dmc.Text("Filters", size="lg"),
            dmc.Button(
                id={"type": Page.RESET_FILTER_BUTTON, "tab": tab},
                children=dmc.Text("Reset", size="sm"),
                variant="subtle",
                color="black",
            ),
        ],
        justify="space-between",
        align="center",
    )
    filter_groups = dmc.Stack(
        [make_filter_group(tab, filter) for filter in Filter],
        id={"type": Page.FILTER_CONTAINER, "tab": tab},
        gap=5,
    )
    footer = dmc.Group(
        dmc.Button(
            "+Add Filter",
            id={"type": Page.ADD_FILTER_BUTTON, "tab": tab},
            variant="outline",
            size="sm",
            color="grey",
        )
    )

    return dmc.Stack([header, filter_groups, footer], gap=10)
