from plotly.graph_objects import Figure

from .enums import Plot


DTICK_CUTOFF = 50


class PlotTransformer:
    def __init__(self):
        """
        Initialize an empty PlotTransformer.
        """
        self.x_field = None
        self.y_field = None
        self.plot_type = None
        self._fig = None

    def initialize(self, df, metadata, plot_type: Plot):
        """
        Populate the PlotTransformer with data and create the plot.

        This method must be called before using any operations on the transformer.
        """

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
        self._create_layout()

    def _create_layout(self):
        """
        Create a starting layout for the current figure.
        """
        layout = {}
        # Set 1 tick per unit if X-axis is small
        if len(self.x_field) < DTICK_CUTOFF:
            layout["xaxis"] = {"dtick": 1}
        self._fig.update_layout(**layout)

    def xlog(self):
        """
        Adds a log scale to the X-axis.
        """
        new_x_title = f"{self._fig.layout.xaxis.title.text} (log scale)"
        self._fig.update_layout(xaxis={"type": "log", "title": new_x_title})

    def ylog(self):
        """
        Adds a log scale to the Y-axis.
        """
        new_y_title = f"{self._fig.layout.yaxis.title.text} (log scale)"
        self._fig.update_layout(yaxis={"type": "log", "title": new_y_title})

    @property
    def figure(self) -> Figure:
        """
        Return the current figure.
        """
        return self._fig
