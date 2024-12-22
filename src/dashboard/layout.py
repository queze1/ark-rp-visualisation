import dash_mantine_components as dmc

from enums import Tab, Text
from dashboard.tabs import make_tab


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

layout = dmc.Container(
    [
        header,
        tabs,
    ],
)