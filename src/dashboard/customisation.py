from enums import Tab, Page
import dash_mantine_components as dmc


def make_customisation_controls(tab: Tab):
    header = dmc.Group(
        [
            dmc.Text("Customisation", size="lg"),
            dmc.Button(
                id={"type": Page.RESET_CUSTOMISATION_BUTTON, "tab": tab},
                children=dmc.Text("Reset", size="sm"),
                variant="subtle",
                color="black",
            ),
        ],
        justify="space-between",
        align="center",
    )

    axes_control = dmc.Grid(
        [
            dmc.GridCol(
                dmc.Text("Axes Options"),
                span=2,
            ),
            dmc.GridCol(
                dmc.Checkbox(
                    id={"type": Page.X_LOG_CHECKBOX, "tab": tab},
                    label="X-Log",
                    checked=False,
                ),
                span=2,
            ),
            dmc.GridCol(
                dmc.Checkbox(
                    id={"type": Page.Y_LOG_CHECKBOX, "tab": tab},
                    label="Y-Log",
                    checked=False,
                ),
                span=2,
            ),
            dmc.GridCol(
                dmc.Checkbox(
                    label="7-Day Moving Avg.",
                ),
                span=3,
            ),
            dmc.GridCol(
                dmc.Checkbox(
                    label="30-Day Moving Avg.",
                ),
                span=3,
            ),
        ],
        align="center",
    )

    title_control = dmc.Grid(
        [
            dmc.GridCol(
                dmc.Text("Title"),
                span=2,
            ),
            dmc.GridCol(
                dmc.TextInput(placeholder="Using default..."),
                span=3,
            ),
        ],
        align="center",
    )

    axes_label_control = dmc.Grid(
        [
            dmc.GridCol(
                dmc.Text("X-Axis Label"),
                span=2,
            ),
            dmc.GridCol(
                dmc.TextInput(placeholder="Using default..."),
                span=3,
            ),
            dmc.GridCol(
                dmc.Text("Y-Axis Label"),
                span=2,
            ),
            dmc.GridCol(
                dmc.TextInput(placeholder="Using default..."),
                span=3,
            ),
        ],
        align="center",
    )

    return dmc.Stack(
        [
            header,
            axes_control,
            title_control,
            axes_label_control,
        ],
        gap=10,
    )
