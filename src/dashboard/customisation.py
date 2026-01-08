import dash_mantine_components as dmc
from dash import Input, Output
from dash.exceptions import PreventUpdate

from dashboard.callback_patterns import (
    match_mavg_7,
    match_mavg_30,
    match_reset_customisation,
    match_sort_axis,
    match_sort_order,
    match_title_input,
    match_x_label,
    match_x_log,
    match_y_label,
    match_y_log,
)
from enums import Page, Tab, Text


def make_customisation_controls(tab: Tab):
    def make_label_col(text):
        return dmc.GridCol(
            dmc.Text(text),
            span=1.5,
        )

    def make_checkbox_col(label, type, span, disabled=False):
        return dmc.GridCol(
            dmc.Checkbox(
                id={"type": type, "tab": tab},
                label=label,
                disabled=disabled,
            ),
            span=span,
        )

    def make_input_col(type):
        return dmc.GridCol(
            dmc.TextInput(
                placeholder="Using default...",
                id={"type": type, "tab": tab},
            ),
            span="auto",
        )

    def make_select_col(type, data):
        return dmc.GridCol(
            dmc.Select(
                id={"type": type, "tab": tab},
                data=data,
                placeholder="Using default...",
            ),
            span="auto",
        )

    header = dmc.Group(
        [
            dmc.Text("Customisation", size="lg"),
            dmc.Button(
                dmc.Text("Reset", size="sm"),
                id={"type": Page.RESET_CUSTOMISATION_BUTTON, "tab": tab},
                variant="subtle",
                color="black",
            ),
        ],
        justify="space-between",
        align="center",
    )

    axes_control = dmc.Grid(
        [
            make_label_col("Axes Options"),
            make_checkbox_col("X-Log", type=Page.X_LOG_CHECKBOX, span=2),
            make_checkbox_col("Y-Log", type=Page.Y_LOG_CHECKBOX, span=2),
            make_checkbox_col(
                "Weekly Moving Avg",
                type=Page.MOVING_AVERAGE_7,
                span=3,
                disabled=tab != Tab.LINE,
            ),
            make_checkbox_col(
                "Monthly Moving Avg",
                type=Page.MOVING_AVERAGE_30,
                span=3,
                disabled=tab != Tab.LINE,
            ),
        ],
        align="center",
    )

    title_control = dmc.Grid(
        [
            make_label_col("Title"),
            make_input_col(Page.TITLE_INPUT),
        ],
        align="center",
    )

    axes_label_control = dmc.Grid(
        [
            make_label_col(f"{Text.X_AXIS} Label"),
            make_input_col(Page.X_LABEL_INPUT),
            make_label_col(f"{Text.Y_AXIS} Label"),
            make_input_col(Page.Y_LABEL_INPUT),
        ],
        align="center",
    )

    sort_control = dmc.Grid(
        [
            make_label_col("Sort By"),
            make_select_col(
                Page.SORT_ORDER_DROPDOWN, data=[Text.ASCENDING, Text.DESCENDING]
            ),
            make_select_col(Page.SORT_AXIS_DROPDOWN, data=[Text.X_AXIS, Text.Y_AXIS]),
        ],
        align="center",
    )

    return dmc.Stack(
        [
            header,
            title_control,
            axes_label_control,
            axes_control,
            sort_control,
        ],
        gap=10,
    )


def register_customisation_callbacks(app):
    def reset_customisation(n_clicks):
        if n_clicks is None:
            raise PreventUpdate

        # Set all options to empty
        return dict(
            title="",
            x_label="",
            y_label="",
            moving_averages={
                7: False,
                30: False,
            },
            sort_order=None,
            sort_axis=None,
            x_log="",
            y_log="",
        )

    app.callback(
        output=dict(
            title=Output(match_title_input, "value"),
            x_label=Output(match_x_label, "value"),
            y_label=Output(match_y_label, "value"),
            moving_averages={
                7: Output(match_mavg_7, "checked"),
                30: Output(match_mavg_30, "checked"),
            },
            sort_order=Output(match_sort_order, "value"),
            sort_axis=Output(match_sort_axis, "value"),
            x_log=Output(match_x_log, "checked"),
            y_log=Output(match_y_log, "checked"),
        ),
        inputs=Input(match_reset_customisation, "n_clicks"),
    )(reset_customisation)
