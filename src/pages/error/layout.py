import dash_mantine_components as dmc
from dash import html


def layout(message: str):
    return dmc.Container(html.P(message))
