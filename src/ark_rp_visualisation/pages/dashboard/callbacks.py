from .customisation import register_customisation_callbacks
from .fields import register_field_callbacks
from .filters import register_filter_callbacks
from .graph_ui import register_graph_callbacks


def register_dashboard_callbacks(app):
    register_field_callbacks(app)
    register_graph_callbacks(app)
    register_filter_callbacks(app)
    register_customisation_callbacks(app)
