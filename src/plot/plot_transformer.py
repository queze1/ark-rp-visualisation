from plotly.graph_objects import Figure

from .enums import Plot


DTICK_CUTOFF = 50


class PlotTransformer:
    def __init__(self, df, metadata, plot_type: Plot):
        if len(df.columns) < 2:
            raise ValueError("Not enough data columns to plot.")

        self.x_field, self.y_field = df.columns[:2]
        self.plot_type = plot_type
        # Create labels and title from metadata
        kwargs = {
            "x": self.x_field,
            "y": self.y_field,
            "labels": {
                self.x_field: metadata[self.x_field]["label"],
                self.y_field: metadata[self.y_field]["label"],
            },
            "title": f"{metadata[self.y_field]['description']} by {metadata[self.x_field]['description']}",
        }

        self._fig = plot_type(df, **kwargs)
        self._fig.update_layout(**self._create_layout())

    def _create_layout(self):
        """
        Create a layout for the current figure.
        """
        layout = {}

        # Set 1 tick per unit if X-axis is small
        if len(self.x_field) < DTICK_CUTOFF:
            layout["xaxis"] = {"dtick": 1}

        return layout

    @property
    def figure(self) -> Figure:
        """
        Return the current figure.
        """
        return self._fig
