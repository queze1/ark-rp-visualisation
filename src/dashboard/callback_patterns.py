from dash import ALL, MATCH

from enums import Page

# Graph patterns
match_graph = {"type": Page.GRAPH, "tab": MATCH}
match_update_graph = {"type": Page.UPDATE_GRAPH_BUTTON, "tab": MATCH}

# Axes patterns
match_axes = {"type": Page.AXIS_TEXT, "tab": MATCH, "index": ALL}
match_swap_axes = {"type": Page.SWAP_AXES_BUTTON, "tab": MATCH}

# Field patterns
match_field_containers = {
    "type": Page.FIELD_AGG_CONTAINER,
    "tab": MATCH,
    "index": ALL,
}
match_fields = {"type": Page.FIELD_DROPDOWN, "tab": MATCH, "index": ALL}
match_agg_containers = {
    "type": Page.FIELD_AGG_CONTAINER,
    "tab": MATCH,
    "index": ALL,
}
match_agg_dropdowns = {"type": Page.FIELD_AGG_DROPDOWN, "tab": MATCH, "index": ALL}
match_agg_spacings = {"type": Page.FIELD_AGG_SPACING, "tab": MATCH, "index": ALL}

# Filter patterns
match_filter_container = {"type": Page.FILTER_CONTAINER, "tab": MATCH}
match_add_filter = {"type": Page.ADD_FILTER_BUTTON, "tab": MATCH}
match_filter_type = {
    "type": Page.FILTER_TYPE,
    "tab": MATCH,
    "index": MATCH,
}
match_filter_types = {
    "type": Page.FILTER_TYPE,
    "tab": MATCH,
    "index": ALL,
}
match_filter_operator = {
    "type": Page.FILTER_OPERATOR,
    "tab": MATCH,
    "index": MATCH,
}
match_filter_operators = {
    "type": Page.FILTER_OPERATOR,
    "tab": MATCH,
    "index": ALL,
}
match_filter_value_container = {
    "type": Page.FILTER_VALUE_CONTAINER,
    "tab": MATCH,
    "index": MATCH,
}
match_filter_values = {
    "type": Page.FILTER_VALUE,
    "tab": MATCH,
    "index": ALL,
}
match_delete_filter = {
    "type": Page.DELETE_FILTER_BUTTON,
    "tab": MATCH,
    "index": ALL,
}
match_reset_filter = {"type": Page.RESET_FILTER_BUTTON, "tab": MATCH}

# Customisation patterns
match_title_input = {"type": Page.TITLE_INPUT, "tab": MATCH}
match_x_label = {"type": Page.X_LABEL_INPUT, "tab": MATCH}
match_y_label = {"type": Page.Y_LABEL_INPUT, "tab": MATCH}
match_x_log = {"type": Page.X_LOG_CHECKBOX, "tab": MATCH}
match_y_log = {"type": Page.Y_LOG_CHECKBOX, "tab": MATCH}
match_mavg_7 = {"type": Page.MOVING_AVERAGE_7, "tab": MATCH}
match_mavg_30 = {"type": Page.MOVING_AVERAGE_30, "tab": MATCH}
match_sort_order = {"type": Page.SORT_ORDER_DROPDOWN, "tab": MATCH}
match_sort_axis = {"type": Page.SORT_AXIS_DROPDOWN, "tab": MATCH}
match_reset_customisation = {"type": Page.RESET_CUSTOMISATION_BUTTON, "tab": MATCH}
