from plotly.graph_objects import Figure

from .metadata import Metadata

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

    def initialize(
        self, df, metadata: Metadata, plot_type: Plot, x_field=None, y_field=None
    ):
        """
        Populate the PlotTransformer with data and create the plot.
        By default, plots by the two most recent fields.

        This method must be called before using any operations on the transformer.
        """

        if len(df.columns) < 2:
            raise ValueError("Not enough data columns to plot.")

        if x_field and y_field:
            self.x_field, self.y_field = x_field, y_field
        else:
            # If either x or y fields are unset, use last two columns
            self.x_field, self.y_field = df.columns[-2:]

        # Create labels and title from metadata
        plot_labels = metadata.generate_plot_labels(self.x_field, self.y_field)
        kwargs = {"x": self.x_field, "y": self.y_field, **plot_labels}

        self.plot_type = plot_type
        self._fig = plot_type(df, **kwargs)
        self._create_layout(df)

    def _create_layout(self, df):
        """
        Create a starting layout for the current figure.
        """
        layout = {}
        # Set 1 tick per unit if X-axis is small
        if len(df[self.x_field]) < DTICK_CUTOFF:
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
