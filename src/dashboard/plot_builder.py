from enums import Operator, Plot
from enums import Field, GroupBy
from data_loader import df


class PlotBuilder:
    def __init__(
        self,
        fields: list[Field],
        filters: list[tuple[Field, Operator, object]],
        x_axis: Field,
        y_axis: Field,
        plot_type: Plot,
    ):
        self._df = df.copy()
        self._fig = None
        self._grouping_field = None
        self._grouped_fields = None
        self._agg_kwargs = None

        self.fields = fields
        self.filters = filters
        self.x_axis = x_axis
        self.y_axis = y_axis
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
        """Sets aggregation kwargs, if not provided, uses default aggregations."""
        if aggregations:
            self._grouped_fields = aggregations.keys()
            # Find the one field which is not aggregated
            (self._grouping_field,) = [
                field for field in self.fields if field not in self._grouped_fields
            ]
            # Create kwargs from supplied aggregations
            self._agg_kwargs = {
                field: (field, aggregation)
                for field, aggregation in aggregations.items()
            }

        else:
            # If aggregations are not supplied, group the rest by the last field
            *self._grouped_fields, self._grouping_field = self.fields
            # Use default aggregations
            self._agg_kwargs = {
                field: (
                    field,
                    GroupBy.NUNIQUE if Field(field).categorical else GroupBy.SUM,
                )
                for field in self._grouped_fields
            }

    def groupby(self):
        """Aggregate and group the current DataFrame."""
        grouped = self._df.groupby(self._grouping_field)[self._grouped_fields]
        self._df = grouped.agg(**self._agg_kwargs).reset_index()

    def sort_default(self):
        # By default, sort by grouped field unless you were grouping by a date
        if not self._grouping_field.temporal:
            self._df = self._df.sort_values(by=self._grouped_fields[0], ascending=True)

    def get_axis_label(self, field: Field):
        if field in self._agg_kwargs:
            _, agg = self._agg_kwargs[field]
            return f"{agg.axis_prefix}{field.axis_label}"
        return field.axis_label

    def get_title_label(self, field: Field):
        if field in self._agg_kwargs:
            _, agg = self._agg_kwargs[field]
            return f"{agg.title_prefix}{field.title_label}"
        return field.title_label

    def make_figure(self):
        primary_field, secondary_field, *tertiary_field = self.fields

        title = f"{self.get_title_label(primary_field)} by {self.get_title_label(secondary_field)}"
        labels = {
            self.x_axis: self.get_axis_label(self.x_axis),
            self.y_axis: self.get_axis_label(self.y_axis),
        }

        self._fig = self.plot_type(
            self._df,
            x=self.x_axis,
            y=self.y_axis,
            title=title,
            labels=labels,
            # Add annotations if 3 vars
            text=tertiary_field[0] if tertiary_field else None,
        )

    def build(self):
        for field in self.fields:
            self.add_field(field)
        for filter in self.filters:
            self.filter(*filter)

        self.set_aggregations()
        self.groupby()
        self.sort_default()
        self.make_figure()
        return self._fig
