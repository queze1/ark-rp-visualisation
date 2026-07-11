import dash_mantine_components as dmc
from dash import dcc, html

from core.enums import Page

layout = dmc.MantineProvider(
    [
        dcc.Location(id=Page.URL, refresh=False),  # pyright: ignore[reportPrivateImportUsage]
        html.Div(id=Page.CONTENT),
    ]
)
