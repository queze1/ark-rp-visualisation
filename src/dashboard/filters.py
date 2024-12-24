from uuid import uuid4
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from enums import Filter, FilterOption, Tab, Page
from data_loader import df

from functools import lru_cache


@lru_cache()
def get_unique(field):
    return sorted(df[field].unique())


# Creates a filter value input
def make_filter_value(filter: Filter, tab: Tab, index):
    select_kwargs = filter.select_kwargs.copy()
    # Check if options need to be loaded dynamically
    if select_kwargs.get("data") == FilterOption.FIELD_UNIQUE:
        select_kwargs["data"] = get_unique(filter)

    return filter.select_input(
        id={
            "type": Page.FILTER_VALUE,
            "tab": tab,
            "index": index,
        },
        **select_kwargs,
    )


def make_filter_group(tab: Tab, filter: Filter):
    # Use random index since filters can be created dynamically
    index = str(uuid4())

    filter_type_select = dmc.Select(
        id={
            "type": Page.FILTER_TYPE,
            "tab": tab,
            "index": index,
        },
        data=[{"label": filter.label, "value": filter} for filter in Filter],
        value=filter,
        maw=200,
    )

    filter_operator_select = dmc.Select(
        id={
            "type": Page.FILTER_OPERATOR,
            "tab": tab,
            "index": index,
        },
        data=filter.operators,
        value=filter.default_operator,
        allowDeselect=False,
        maw=100,
    )

    delete_filter_button = dmc.ActionIcon(
        DashIconify(icon="streamline:delete-1-solid", width=12),
        id={"type": Page.DELETE_FILTER_BUTTON, "tab": tab, "index": index},
        variant="outline",
        color="red",
        size="sm",
        # To match select height
        my=7,
    )

    return dmc.Grid(
        [
            dmc.GridCol(
                filter_type_select,
                span="content",
            ),
            dmc.GridCol(
                filter_operator_select,
                span="content",
            ),
            dmc.GridCol(
                make_filter_value(filter, tab, index),
                id={"type": Page.FILTER_VALUE_CONTAINER, "tab": tab, "index": index},
                span="auto",
            ),
            dmc.GridCol(delete_filter_button, span="content"),
        ],
        id={"type": Page.FILTER_GROUP_CONTAINER, "tab": tab, "index": index},
    )


def make_default_filters(tab):
    # Creates one of every possible filter
    return [make_filter_group(tab, filter) for filter in Filter]


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
        make_default_filters(tab),
        id={"type": Page.FILTER_CONTAINER, "tab": tab},
        gap=5,
    )
    footer = dmc.Group(
        dmc.Button(
            "+ Add Filter",
            id={"type": Page.ADD_FILTER_BUTTON, "tab": tab},
            variant="outline",
            size="sm",
            color="grey",
        ),
    )

    return dmc.Stack(
        [header, dmc.Space(h=10), filter_groups, dmc.Space(h=15), footer], gap=0
    )
