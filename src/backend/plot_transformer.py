from plotly.graph_objects import Figure
import pandas as pd

from .enums import Plot, Field
from .metadata import Metadata

DTICK_CUTOFF = 50


class PlotTransformer:
    """
    Class which creates and manipulates a plot using a series of operations.
    """

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
        kwargs = {
            "x": self.x_field,
            "y": self.y_field,
            **metadata.generate_plot_labels(self.x_field, self.y_field),
            **self._generate_annotations(df, plot_type),
        }

        self.plot_type = plot_type
        self._fig = plot_type(df, **kwargs)
        self._create_layout(df, plot_type)

    def _create_layout(self, df, plot_type: Plot):
        """
        Create a starting layout for the current figure.
        """
        # Set 1 tick per unit if X-axis is small
        if len(df[self.x_field]) < DTICK_CUTOFF:
            self._fig.update_layout(xaxis={"dtick": 1})

        # Format annotations if scatter
        if plot_type == Plot.SCATTER:
            self._fig.update_traces(textposition="top center", textfont_size=10)

    def _generate_annotations(self, df, plot_type: Plot):
        """
        Generate annotations for scatter plots.
        """
        if len(df.columns) <= 2 or plot_type != Plot.SCATTER:
            return {}

        # Assume the grouping field is any third column
        grouping_field = df.columns.difference([self.x_field, self.y_field])[0]
        return {"text": df[grouping_field]}

    def xlog(self):
        """
        Adds a log scale to the X-axis.
        """
        if self._fig is None:
            raise ValueError("Figure has not been initialized yet.")

        new_x_title = f"{self._fig.layout.xaxis.title.text} (log scale)"
        self._fig.update_layout(xaxis={"type": "log", "title": new_x_title})

    def ylog(self):
        """
        Adds a log scale to the Y-axis.
        """
        if self._fig is None:
            raise ValueError("Figure has not been initialized yet.")

        new_y_title = f"{self._fig.layout.yaxis.title.text} (log scale)"
        self._fig.update_layout(yaxis={"type": "log", "title": new_y_title})

    def add_moving_average_line(self, window: int, label: str = None):
        """
        Adds a new line trace for a moving average of the Y-axis.

        Parameters:
        - window: The window size (e.g., 7 for weekly, 30 for monthly).
        - label: Optional label for the trace in the legend. Defaults to "Weekly/Monthly Moving Avg", or "(window)-Day Moving Avg".
        """
        if self._fig is None:
            raise ValueError("Figure has not been initialized yet.")
        if self.x_field != Field.DATE:
            raise ValueError("Invalid X-axis, must be date.")
        if self.plot_type != Plot.LINE:
            raise ValueError("Invalid plot type, must be line.")

        # Calculate the rolling average
        x_values = self._fig.data[0].x
        y_values = pd.Series(self._fig.data[0].y)
        ma_values = y_values.rolling(window=window, min_periods=3).mean()

        if label is None:
            periods = {7: "Weekly", 30: "Monthly"}
            label = f"{periods.get(window, f'{window}-Day')} Moving Avg"

        # Add a new trace for the moving average
        self._fig.add_trace(
            dict(
                x=x_values,
                y=ma_values,
                mode="lines",
                name=label,
                line=dict(dash="dot"),
            )
        )

        # Add legend if not added already
        self._fig.update_traces(selector=0, name="Daily", showlegend=True)
        return self

    @property
    def figure(self) -> Figure:
        """
        Return the current figure.
        """
        return self._fig
