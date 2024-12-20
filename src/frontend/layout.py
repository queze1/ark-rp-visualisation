import dash_mantine_components as dmc
from dash import dcc

from enums import Tab, PageText
from frontend.controls import make_controls

tabs = dmc.Tabs(
    [
        dmc.TabsList([dmc.TabsTab(tab.label, value=tab) for tab in Tab]),
    ]
    + [dmc.TabsPanel(make_controls(tab), value=tab) for tab in Tab],
    id="tabs",
    value=Tab.LINE,
)

layout = dmc.Container(
    [
        dmc.Stack(
            [
                dmc.Title(PageText.TITLE),
                dmc.Text(PageText.EXPLAINER),
            ],
            mt=10,
            mb=20,
            gap=10,
        ),
        tabs,
        dcc.Graph(id="graph"),
    ]
)
