import dash

from core.enums import Text

from . import callbacks
from .layout import layout


def register_dashboard():
    dash.register_page(
        __name__, path="/", name="Dashboard", title=Text.TITLE, layout=layout
    )
