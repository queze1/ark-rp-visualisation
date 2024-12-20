import dash_mantine_components as dmc

from frontend.controls import make_controls


def make_tabs(tabs, starting_tab):
    return dmc.Tabs(
        [
            dmc.TabsList(
                [
                    dmc.TabsTab(tab_dict["label"], value=tab_id)
                    for tab_id, tab_dict in tabs.items()
                ]
            ),
        ]
        + [dmc.TabsPanel(make_controls(tab_id), value=tab_id) for tab_id in tabs],
        id="tabs",
        value=starting_tab,
    )
