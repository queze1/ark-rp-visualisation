from dashboard.customisation import register_customisation_callbacks
from dashboard.fields import register_field_callbacks
from dashboard.filters import (
    register_filter_callbacks,
)
from dashboard.graph_engine import (
    register_graph_callbacks,
)


def register_callbacks(app):
    register_field_callbacks(app)
    register_graph_callbacks(app)
    register_filter_callbacks(app)
    register_customisation_callbacks(app)
