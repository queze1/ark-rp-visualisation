import pandas as pd

from enums import Plot
from pipeline.enums import Field, GroupBy


class PlotBuilder:
    def __init__(self, df: pd.DataFrame):
        self._df = df.copy()
        self._fields = []

    def add_field(self, field: Field, reaction: str = None):
        # Check if `field` is a field by calling it
        field = Field(field)

        # Create new derivative fields if needed
        if reaction and field is Field.REACTION_COUNT:
            self._df[field] = [d.get(reaction, 0) for d in self._df[Field.REACTIONS]]
        elif reaction:
            # If a specific reaction was specified but the field was not for reactions, raise an exception
            raise ValueError("Invalid field for reaction counts")
        elif field is Field.HOUR:
            self._df[field] = self._df[Field.DATE].dt.hour
        elif field is Field.DAY:
            self._df[field] = self._df[Field.DATE].dt.day
        elif field is Field.DATE:
            self._df[field] = self._df[Field.DATE].dt.date
        elif field is Field.REACTION_COUNT:
            self._df[field] = [
                max(d.values(), default=0) for d in self._df[Field.REACTIONS]
            ]
        elif field is Field.COUNT:
            # For counting messages, intended to be combined with `.sum`
            self._df[field] = 1

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

    def sort(self, field: Field, ascending: bool = True):
        self._df = self._df.sort_values(by=field, ascending=ascending)
        return self

    def plot(
        self,
        fields: list[Field],
        x_axis: Field,
        y_axis: Field,
        plot_type: Plot,
    ):
        for field in fields:
            self.add_field(field)
        # Group and aggregate using default settings
        self.group_by_multiple()

        # By default, sort by grouped field unless you were grouping by a date
        grouped_field, *_, grouping_field = fields
        if not Field(grouping_field).temporal:
            self.sort(field=grouped_field)
        return Plot(plot_type)(self._df, x=x_axis, y=y_axis)
