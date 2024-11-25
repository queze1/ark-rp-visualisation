from plotly.graph_objects import Figure

from .enums import Field, Plot


class PlotTransformer:
    def __init__(self, df, history, plot_type: Plot):
        if len(df.columns) < 2:
            raise ValueError("Not enough data columns to plot.")

        # Track the x and y fields to be used for plotting
        self.x_field, self.y_field = df.columns[:2]
        self.plot_type = plot_type
        self.history = history
        kwargs = {
            "x": self.x_field,
            "y": self.y_field,
            **self._generate_labels_and_title(),
        }

        self._fig = plot_type(df, **kwargs)
        self._fig.update_layout(**self._create_layout())

    @staticmethod
    def _field_friendly_name(field: str) -> str:
        """
        Convert a field name into a friendly, human-readable name.
        """
        if field == Field.COUNT:
            return "Messages"
        elif field == Field.HOUR:
            return "Hour of Day"
        elif field == Field.DAY:
            return "Day of Month"
        return field.replace("_", " ").title()

    def _generate_labels_and_title(self):
        x_label, y_label = map(self._field_friendly_name, (self.x_field, self.y_field))

        kwargs = {
            "labels": {self.x_field: x_label, self.y_field: y_label},
            "title": None,
        }

        # TODO: Figure out axis and title metadata setting

        return kwargs

    def _create_layout(self):
        """
        Create a history-based layout for the current figure.
        """
        layout = {}

        # If the x-axis is HOUR, DAY, or REACTION_COUNT, show ticks every unit (categorical & numerical)
        if self.x_field in {Field.HOUR, Field.DAY, Field.REACTION_COUNT}:
            layout["xaxis"] = {"dtick": 1}

        return layout

    @property
    def figure(self) -> Figure:
        """
        Return the current figure.
        """
        return self._fig
