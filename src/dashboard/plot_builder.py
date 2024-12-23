from enums import Operator, Plot
from pipeline.enums import Field, GroupBy
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
        self.df = df.copy()
        self.fig = None
        self.fields = fields
        self.filters = filters
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.plot_type = plot_type

    def add_field(self, field: Field):
        # Create the field if it doesn't already exist
        if field in self.df:
            return

        if field == Field.HOUR:
            self.df[field] = self.df[Field.DATETIME].dt.hour
        elif field == Field.DAY:
            self.df[field] = self.df[Field.DATETIME].dt.day
        elif field == Field.DATE:
            self.df[field] = self.df[Field.DATETIME].dt.date
        elif field == Field.COUNT:
            self.df[field] = 1

    def filter(self, field: Field, operator: Operator, value):
        self.add_field(field)
        self.df = self.df[operator(self.df[field], value)]

    def group_by_multiple(self, aggregations: dict[Field, GroupBy] = {}):
        """
        Aggregate multiple fields by the specified operations.
        """
        if aggregations:
            rest = aggregations.keys()
            # Find the one field which is not aggregated
            (grouping_field,) = [field for field in self.fields if field not in rest]

            # Create kwargs from supplied aggregations
            kwargs = {
                field: (field, aggregation)
                for field, aggregation in aggregations.items()
            }
        else:
            # If aggregations are not supplied, group the rest by the last field
            *rest, grouping_field = self.fields

            # Use default aggregations
            kwargs = {
                field: (
                    field,
                    GroupBy.NUNIQUE if Field(field).categorical else GroupBy.SUM,
                )
                for field in rest
            }

        grouped = self.df.groupby(grouping_field)[rest]
        self.df = grouped.agg(**kwargs).reset_index()

    def sort_default(self):
        # By default, sort by grouped field unless you were grouping by a date
        grouped_field, *_, grouping_field = self.fields
        if not grouping_field.temporal:
            self.df = self.df.sort_values(by=grouped_field, ascending=True)

    def make_figure(self):
        primary_field, secondary_field, *tertiary_field = self.fields
        title = f"{primary_field.label} by {secondary_field.label}"
        labels = {self.x_axis: self.x_axis.label, self.y_axis: self.y_axis.label}

        self.fig = self.plot_type(
            self.df,
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

        # Group and aggregate using default settings
        self.group_by_multiple()
        self.sort_default()
        self.make_figure()
        return self.fig
