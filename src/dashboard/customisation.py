from enums import Tab, Page
import dash_mantine_components as dmc


def make_customisation_controls(tab: Tab):
    def make_label_col(text):
        return dmc.GridCol(
            dmc.Text(text),
            span=2,
        )

    def make_checkbox_col(label, type, span):
        return dmc.GridCol(
            dmc.Checkbox(
                id={"type": type, "tab": tab},
                label=label,
                checked=False,
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
            make_checkbox_col("7-Day Moving Avg", type=Page.MOVING_AVERAGE_7, span=3),
            make_checkbox_col("30-Day Moving Avg", type=Page.MOVING_AVERAGE_30, span=3),
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
            make_label_col("X-Axis Label"),
            make_input_col(Page.X_LABEL_INPUT),
            make_label_col("Y-Axis Label"),
            make_input_col(Page.Y_LABEL_INPUT),
        ],
        align="center",
    )

    sort_control = dmc.Grid(
        [
            make_label_col("Sort By"),
            make_select_col(Page.SORT_ORDER_DROPDOWN, data=["ascending", "descending"]),
            make_select_col(Page.SORT_AXIS_DROPDOWN, data=["X-Axis", "Y-Axis"]),
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
