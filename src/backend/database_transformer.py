import pandas as pd

from .enums import Field, Filter, GroupBy
from .metadata import Metadata


class DatabaseTransformer:
    """
    Class which manipulates a DataFrame using a series of operations.

    On initialisation, starts with a fully populated DataFrame, to allow for "pre-filtering", filters on the initial data.
    e.g. Filtering by "author", then plotting messages by date.

    "Adding" new fields pushes them onto `_fields`, to indicate the fields to be exported in the final output,
    and the default order of operations. Generally, important/independent/X-axis fields are oldest/first, while
    dependent/Y-axis fields are latest.

    When an operation needs to edit columns (e.g. groupby, value counts), they drop all columns not on `_fields`,
    then do the operation. "Post-filtering" on output data can use the same logic as when "pre-filtering".

    Field metadata (e.g. automatic titling/labelling) is handled by `Metadata`.
    """

    def __init__(self, df: pd.DataFrame):
        self._original = df
        self._df = df.copy()
        # Helper list of fields on the current "stack"
        self._fields = []
        self._metadata = Metadata()

    def add_field(self, field: Field, reaction: str = None):
        # Check if `field` is a field by calling it
        field = Field(field)

        # Create new derivative fields if needed
        if reaction and field is Field.REACTION_COUNT:
            self._df[field] = [d.get(reaction, 0) for d in self._df[Field.REACTIONS]]
        elif reaction:
            # If a specific reaction was specified but the field was not for reactions, raise an exception
            # TODO: Integrate better with metadata and enums, enums are immutable
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

        # Add metadata
        for grouped_field, aggregation in aggregations.items():
            self._metadata.add_group_by(grouped_field, aggregation)
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

    def value_counts(self):
        """
        Special case of group-by: Value counts of a single field.
        By default, sorts in ascending order of count.
        """
        (field,) = self._fields
        counts = self._df[field].value_counts()
        self._df = counts.reset_index()

        # Equivalent to grouping by and summing Field.COUNT
        self._metadata.add_group_by(Field.COUNT, GroupBy.SUM)
        return self

    def cumulative(self, field: Field, result_field=None):
        """
        Generate a field's cumulative sum if numeric, or its index otherwise.

        By default, the result field is of the format f"cumulative_{field}".
        """
        if result_field is None:
            result_field = f"cumulative_{field}"

        if pd.api.types.is_numeric_dtype(self._df[field]):
            # Generate cumulative sum
            cumulative_values = self._df[field].cumsum()
        else:
            # Generate index
            cumulative_values = range(1, len(self._df) + 1)

        # Insert the result as a new column
        self._df.insert(
            loc=self._df.columns.get_loc(field) + 1,
            column=result_field,
            value=cumulative_values,
        )

        self._metadata.add_cumulative(field, result_field)
        return self

    def sort(self, field: Field, ascending: bool = True):
        self._df = self._df.sort_values(by=field, ascending=ascending)
        return self

    def filter(self, filter: Filter, field: Field, value):
        """
        Apply a filter to the DataFrame.
        """
        self._df = self._df[filter(self._df[field], value)]
        self._metadata.add_filter(filter, field, value)
        return self

    @property
    def dataframe(self) -> pd.DataFrame:
        """
        Return the current DataFrame.
        """
        return self._df

    @property
    def metadata(self) -> Metadata:
        """
        Return the current DataFrame's metadata.
        """
        return self._metadata

    def reset(self):
        """
        Reset current state.
        """
        self._df = self._original.copy()
        self._fields = []
        self._metadata = Metadata()
