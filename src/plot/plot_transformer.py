from .enums import Plot
from plotly.graph_objects import Figure


class PlotTransformer:
    def __init__(self, df, history, plot_type: Plot):
        if len(df.columns) < 2:
            raise ValueError("Not enough data columns to plot.")

        x_field, y_field = df.columns[:2]
        kwargs = {"x": x_field, "y": y_field, **self._generate_labels(history)}
        self._fig = plot_type(df, **kwargs)

    @staticmethod
    def _generate_labels(history):
        """
        Generate history-based labels for a figure.
        """
        return {
            "title": " vs. ".join(
                op["field"] for op in history if op["operation"] == "add_field"
            ),
        }

    @property
    def figure(self) -> Figure:
        """
        Return the current figure.
        """
        return self._fig
