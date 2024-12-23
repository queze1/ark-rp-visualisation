import pandas as pd

from enums import Operator, Plot
from pipeline.enums import Field, GroupBy


class PlotBuilder:
    def __init__(self, df: pd.DataFrame):
        self._df = df.copy()
        self._fields = []

    def add_field(self, field: Field, append=True):
        # Check if `field` is a field by calling it
        field = Field(field)

        # Create new derivative fields if needed
        if field is Field.HOUR:
            self._df[field] = self._df[Field.DATETIME].dt.hour
        elif field is Field.DAY:
            self._df[field] = self._df[Field.DATETIME].dt.day
        elif field is Field.DATE:
            self._df[field] = self._df[Field.DATETIME].dt.date
        elif field is Field.COUNT:
            # For counting messages, intended to be combined with `.sum`
            self._df[field] = 1

        if append:
            self._fields.append(field)
        return self

    def group_by_multiple(self, aggregations: dict[Field, GroupBy] = {}):
        """
        Aggregate multiple fields by the specified operations.
        """
        # Drop extraneous columns
        self._df = self._df[self._fields]

        if aggregations:
            # Find the (one) field which is not aggregated
            (grouping_field,) = self._df.columns.difference(aggregations.keys())
            rest = self._df.columns[self._df.columns != grouping_field]

            # Create kwargs from supplied aggregations
            kwargs = {
                field: (field, aggregation)
                for field, aggregation in aggregations.items()
            }
        else:
            # If aggregations are not supplied, group the rest by the last field
            *rest, grouping_field = self._fields

            # Use default aggregations
            kwargs = {
                field: (
                    field,
                    GroupBy.NUNIQUE if Field(field).categorical else GroupBy.SUM,
                )
                for field in rest
            }

        grouped = self._df.groupby(grouping_field)[rest]
        self._df = grouped.agg(**kwargs).reset_index()
        return self

    def filter(self, field: Field, operator: Operator, value):
        # Create field if it doesn't already exist
        self.add_field(field, append=False)
        self._df = self._df[operator(self._df[field], value)]
        return self

    def sort(self, field: Field, ascending: bool = True):
        self._df = self._df.sort_values(by=field, ascending=ascending)
        return self

    def generate_title(self):
        primary_field, secondary_field, *_ = self._fields
        return f"{primary_field.label} by {secondary_field.label}"

    def plot(
        self,
        fields: list[Field],
        filters: list[tuple[Field, Operator, object]],
        x_axis: Field,
        y_axis: Field,
        plot_type: Plot,
    ):
        for field in fields:
            self.add_field(field)
        for filter in filters:
            self.filter(*filter)

        # Group and aggregate using default settings
        self.group_by_multiple()

        # By default, sort by grouped field unless you were grouping by a date
        grouped_field, *_, grouping_field = fields
        if not grouping_field.temporal:
            self.sort(field=grouped_field)

        labels = {x_axis: x_axis.label, y_axis: y_axis.label}
        fig = plot_type(
            self._df,
            x=x_axis,
            y=y_axis,
            labels=labels,
            title=self.generate_title(),
            # Add annotations if 3 vars
            text=self._df[grouping_field] if len(fields) == 3 else None,
        )
        return fig
