from enums import Tab, Page
import dash_mantine_components as dmc


def make_customisation_controls(tab: Tab):
    def make_label_col(text):
        return dmc.GridCol(
            dmc.Text(text),
            span=2,
        )

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
            make_label_col("Axes Options"),
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
            make_label_col("Title"),
            dmc.GridCol(
                dmc.TextInput(placeholder="Using default..."),
                span="auto",
            ),
        ],
        align="center",
    )

    axes_label_control = dmc.Grid(
        [
            make_label_col("X-Axis Label"),
            dmc.GridCol(
                dmc.TextInput(placeholder="Using default..."),
                span="auto",
            ),
            make_label_col("Y-Axis Label"),
            dmc.GridCol(
                dmc.TextInput(placeholder="Using default..."),
                span="auto",
            ),
        ],
        align="center",
    )

    sort_control = dmc.Grid(
        [
            make_label_col("Sort By"),
            dmc.GridCol(
                dmc.Select(
                    data=["ascending", "descending"], placeholder="Using default..."
                ),
                span="auto",
            ),
            dmc.GridCol(
                dmc.Select(data=["X-Axis", "Y-Axis"], placeholder="Using default..."),
                span="auto",
            ),
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
