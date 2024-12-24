from enums import Operator, Plot
from enums import Field, GroupBy
from data_loader import df

DTICK_CUTOFF = 50


class PlotBuilder:
    def __init__(
        self,
        fields: list[Field],
        filters: list[tuple[Field, Operator, object]],
        x_axis: Field,
        y_axis: Field,
        x_log: bool,
        y_log: bool,
        plot_type: Plot,
    ):
        self._df = df.copy()
        self._fig = None
        self._grouping_field = None
        self._grouped_fields = None
        self._aggregations = None

        self.fields = fields
        self.filters = filters
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.x_log = x_log
        self.y_log = y_log
        self.plot_type = plot_type

    def add_field(self, field: Field):
        # Create the field if it doesn't already exist
        if field in self._df:
            return

        if field == Field.HOUR:
            self._df[field] = self._df[Field.DATETIME].dt.hour
        elif field == Field.DAY:
            self._df[field] = self._df[Field.DATETIME].dt.day
        elif field == Field.DATE:
            self._df[field] = self._df[Field.DATETIME].dt.date
        elif field == Field.COUNT:
            self._df[field] = 1

    def filter(self, field: Field, operator: Operator, value):
        self.add_field(field)
        self._df = self._df[operator(self._df[field], value)]

    def set_aggregations(self, aggregations: dict[Field, GroupBy] = {}):
        """Sets aggregations, if not provided, uses default aggregations."""
        if aggregations:
            self._grouped_fields = aggregations.keys()
            # Find the one field which is not aggregated
            (self._grouping_field,) = [
                field for field in self.fields if field not in self._grouped_fields
            ]
            self._aggregations = aggregations

        else:
            # If aggregations are not supplied, group the rest by the last field
            *self._grouped_fields, self._grouping_field = self.fields
            # Use default aggregations
            self._aggregations = {
                field: GroupBy.NUNIQUE if Field(field).categorical else GroupBy.SUM
                for field in self._grouped_fields
            }

    def groupby(self):
        """Aggregate and group the current DataFrame."""
        grouped = self._df.groupby(self._grouping_field)[self._grouped_fields]
        self._df = grouped.agg(
            **{
                field: (field, aggregation)
                for field, aggregation in self._aggregations.items()
            }
        ).reset_index()

    def sort_default(self):
        # By default, sort by grouped field unless you were grouping by a date
        if not self._grouping_field.temporal:
            self._df = self._df.sort_values(by=self._grouped_fields[0], ascending=True)

    def get_label(self, field: Field, label_type="axis"):
        """
        Returns the label for a Field with aggregation prefixes.
        """
        label = field.axis_label if label_type == "axis" else field.title_label

        # If aggregation exists, add its prefix
        if field in self._aggregations:
            agg = self._aggregations[field]
            prefix = agg.axis_prefix if label_type == "axis" else agg.title_prefix
            return prefix + label
        return label

    def get_axis_label(self, field: Field):
        return self.get_label(field, label_type="axis")

    def get_title_label(self, field: Field):
        return self.get_label(field, label_type="title")

    def make_figure(self):
        primary_field, secondary_field, *tertiary_field = self.fields
        title = f"{self.get_title_label(primary_field)} by {self.get_title_label(secondary_field)}"
        labels = {field: self.get_axis_label(field) for field in self.fields}

        self._fig = self.plot_type(
            self._df,
            x=self.x_axis,
            y=self.y_axis,
            title=title,
            labels=labels,
            log_x=self.x_log,
            log_y=self.y_log,
            # Add annotations if 3 vars
            text=tertiary_field[0] if tertiary_field else None,
        )

    def format_figure(self):
        """
        Apply formatting to the current figure.
        """
        layout_kwargs = {}

        # Set 1 tick per unit if bar plot and X-axis is hour or day
        if self.x_axis in {Field.HOUR, Field.DAY} and self.plot_type == Plot.SCATTER:
            layout_kwargs["xaxis"] = dict(dtick=1)

        # Update titles if log scale
        if self.x_log:
            new_title = f"{self._fig.layout.xaxis.title.text} (log scale)"
            layout_kwargs.setdefault("xaxis", {})["title"] = new_title
        if self.y_log:
            new_title = f"{self._fig.layout.yaxis.title.text} (log scale)"
            layout_kwargs.setdefault("yaxis", {})["title"] = new_title

        # Apply combined layout
        self._fig.update_layout(**layout_kwargs)

        # Format annotations if scatter plot
        if self.plot_type == Plot.SCATTER:
            self._fig.update_traces(textposition="top center", textfont_size=10)

    def build(self):
        for field in self.fields:
            self.add_field(field)
        for filter in self.filters:
            self.filter(*filter)

        self.set_aggregations()
        self.groupby()
        self.sort_default()
        self.make_figure()
        self.format_figure()
        return self._fig
