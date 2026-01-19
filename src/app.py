import dash_mantine_components as dmc
from dash import Dash, _dash_renderer, page_container

from core.enums import Text
from pages.dashboard import register_dashboard

# Required for DMC 0.14+
_dash_renderer._set_react_version("18.2.0")

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=dmc.styles.ALL,
    prevent_initial_callbacks=True,
)
app.title = Text.TITLE
app.layout = dmc.MantineProvider(page_container)

register_dashboard()

if __name__ == "__main__":
    app.run(debug=True)
