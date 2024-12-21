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

    def group_by_multiple(self, aggregations: dict[Field, GroupBy]):
        """
        Aggregate multiple fields by the specified operations.
        """
        # Drop extraneous columns
        self._df = self._df[self._fields]

        # Find the (one) field which is not aggregated
        (field,) = self._df.columns.difference(aggregations.keys())
        rest = self._df.columns[self._df.columns != field]

        grouped = self._df.groupby(field)[rest]
        kwargs = {
            grouped_field: (grouped_field, aggregation)
            for grouped_field, aggregation in aggregations.items()
        }
        self._df = grouped.agg(**kwargs).reset_index()
        return self

    def group_by(self, aggregation: GroupBy, field=None):
        """
        Group by a field and aggregate with the specified operation.
        By default, groups by the oldest field and sorts in ascending order of group.
        """
        if field:
            rest = [
                grouped_field
                for grouped_field in self._fields
                if grouped_field != field
            ]
        else:
            field, *rest = self._fields

        # Reuse logic in `group_by_multiple`
        aggregations = {grouped_field: aggregation for grouped_field in rest}
        return self.group_by_multiple(aggregations)

    def sort(self, field: Field, ascending: bool = True):
        self._df = self._df.sort_values(by=field, ascending=ascending)
        return self

    def plot(
        self,
        primary_field: Field,
        secondary_field: Field,
        x_axis: Field,
        y_axis: Field,
        plot_type: Plot,
    ):
        self.add_field(primary_field)
        self.add_field(secondary_field)
        self.group_by(
            GroupBy.NUNIQUE if Field(secondary_field).categorical else GroupBy.SUM
        )
        # By default, sort by summary value unless you were grouping by a date
        self.sort(primary_field if Field(primary_field).temporal else secondary_field)
        return Plot(plot_type)(self._df, x=x_axis, y=y_axis)
