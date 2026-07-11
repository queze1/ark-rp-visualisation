import dash_mantine_components as dmc
from dash import dcc
from dash_iconify import DashIconify

from core.enums import Page, Tab, Text

from .customisation import make_customisation_controls
from .fields import make_field_controls
from .filters import make_filter_controls


def make_tab(tab: Tab):
    return dmc.Card(
        [
            make_field_controls(tab),
            dmc.Divider(mt=25, mb=15),
            make_filter_controls(tab),
            dmc.Divider(mt=25, mb=15),
            make_customisation_controls(tab),
            dmc.Space(h=20),
            # --- ACTION ROW ---
            dmc.Group(
                [
                    # Fullscreen button
                    dmc.Anchor(
                        dmc.ActionIcon(
                            DashIconify(icon="lucide:maximize", width=20),
                            id={"type": Page.FULLSCREEN_BUTTON_ICON, "tab": tab},
                            variant="light",
                            size="lg",
                            color="blue",
                            disabled=True,
                        ),
                        id={"type": Page.FULLSCREEN_BUTTON, "tab": tab},
                        href="#",
                        target="_blank",
                        underline=False,
                    ),
                    # Update graph button
                    dmc.Button(
                        Text.UPDATE_GRAPH_LABEL,
                        id={"type": Page.UPDATE_GRAPH_BUTTON, "tab": tab},
                    ),
                ],
                justify="flex-end",
                gap="sm",
            ),
            dmc.Space(h=20),
            dcc.Loading(  # pyright: ignore[reportPrivateImportUsage]
                dcc.Graph(  # pyright: ignore[reportPrivateImportUsage]
                    id={"type": Page.GRAPH, "tab": tab},
                ),
                type="default",
                delay_hide=500,
            ),
        ],
        withBorder=True,
    )
