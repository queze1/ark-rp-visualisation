import dash_mantine_components as dmc
from dash import html

from dashboard.tabs import make_tab
from enums import Tab, Text

header = dmc.Stack(
    [
        dmc.Title(Text.TITLE),
        dmc.Text(Text.EXPLAINER),
    ],
    mt=10,
    mb=20,
    gap=10,
)


tabs = dmc.Tabs(
    [
        dmc.TabsList([dmc.TabsTab(tab.label, value=tab) for tab in Tab]),
    ]
    + [dmc.TabsPanel(make_tab(tab), value=tab) for tab in Tab],
    value=Tab.LINE,
)

footer = html.Footer(
    dmc.Stack(
        [
            dmc.Group(
                [
                    dmc.Text(
                        "Retrieved 25 December 2024.",
                        size="xs",
                        c="dimmed",
                    ),
                    dmc.Anchor(
                        "Github",
                        href="https://github.com/queze1/ark-rp-visualisation",
                        size="xs",
                        c="dimmed",
                    ),
                ],
                justify="space-between",
            ),
            dmc.Text(
                [
                    "Made by ",
                    html.Strong("queze"),
                    ", message on TTGSOC Discord for bugs and suggestions",
                ],
                size="xs",
                c="dimmed",
            ),
        ],
        my=10,
        gap=5,
    )
)

layout = dmc.Container(
    [
        header,
        tabs,
        footer,
    ],
)
