from functools import lru_cache
from uuid import uuid4

import dash_mantine_components as dmc
from dash import Input, Output, Patch, State, ctx
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from dashboard.callback_patterns import (
    match_add_filter,
    match_delete_filter,
    match_filter_container,
    match_filter_operator,
    match_filter_type,
    match_filter_value_container,
    match_reset_filter,
)
from data_loader import DataLoader
from enums import Filter, FilterOption, Page, Tab

df = DataLoader().df


@lru_cache()
def get_unique(field):
    return sorted(df[field].unique())


def make_filter_value_input(filter: Filter, tab: Tab, index):
    select_kwargs = filter.select_kwargs.copy()
    # Check if options need to be loaded dynamically
    if select_kwargs.get("data") == FilterOption.FIELD_UNIQUE:
        select_kwargs["data"] = get_unique(filter)

    return filter.select_input(
        id={
            "type": Page.FILTER_VALUE_INPUT,
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
                make_filter_value_input(filter, tab, index),
                id={"type": Page.FILTER_VALUE_CONTAINER, "tab": tab, "index": index},
                span="auto",
            ),
            dmc.GridCol(delete_filter_button, span="content"),
        ],
        id={"type": Page.FILTER_GROUP_CONTAINER, "tab": tab, "index": index},
    )


def make_default_filters(tab):
    # Create one of every possible filter
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


def register_filter_callbacks(app):
    # Callback to reset filters
    def reset_filters(n_clicks):
        if n_clicks is None or not ctx.triggered_id:
            raise PreventUpdate

        tab = Tab(ctx.triggered_id["tab"])
        return make_default_filters(tab)

    app.callback(
        Output(match_filter_container, "children", allow_duplicate=True),
        Input(match_reset_filter, "n_clicks"),
    )(reset_filters)

    # Callback to add a new filter
    def add_filter(n_clicks):
        if n_clicks is None or not ctx.triggered_id:
            raise PreventUpdate

        tab = Tab(ctx.triggered_id["tab"])
        patched_children = Patch()
        patched_children.append(make_filter_group(tab, Filter.DATE))
        return patched_children

    app.callback(
        Output(match_filter_container, "children", allow_duplicate=True),
        Input(match_add_filter, "n_clicks"),
    )(add_filter)

    # Callback to update filter options
    def update_filter_options(filter_type):
        c = ctx.triggered_id
        if not c:
            return

        filter_type = Filter(filter_type)
        tab, index = c["tab"], c["index"]
        return (
            filter_type.operators,
            filter_type.default_operator,
            make_filter_value_input(filter_type, tab, index),
        )

    app.callback(
        Output(
            match_filter_operator,
            "data",
        ),
        Output(
            match_filter_operator,
            "value",
        ),
        Output(
            match_filter_value_container,
            "children",
        ),
        Input(
            match_filter_type,
            "value",
        ),
    )(update_filter_options)

    # Callback to delete a filter group
    def delete_filter(n_clicks, children):
        if not any(n_clicks) or not ctx.triggered_id:
            raise PreventUpdate

        # Find the filter group with same index and get its position in children
        index = ctx.triggered_id["index"]
        (filter_index,) = [
            i
            for i, child in enumerate(children)
            if child["props"]["id"]["index"] == index
        ]

        # Delete the filter group from children
        patched_children = Patch()
        del patched_children[filter_index]
        return patched_children

    app.callback(
        Output(match_filter_container, "children", allow_duplicate=True),
        Input(match_delete_filter, "n_clicks"),
        State(match_filter_container, "children"),
    )(delete_filter)
