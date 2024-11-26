import pandas as pd

from .metadata import Metadata
from .enums import Field, GroupBy


class DatabaseTransformer:
    """
    Transformer which manipulates a DataFrame using a series of operations.
    """

    def __init__(self, df: pd.DataFrame):
        self._df = df
        self._current = pd.DataFrame()
        self._metadata = Metadata()

    def add_field(self, field: Field):
        if field == Field.HOUR:
            new_column = self._df[Field.DATE].dt.hour
        elif field == Field.DAY:
            new_column = self._df[Field.DATE].dt.day
        elif field == Field.DATE:
            new_column = self._df[Field.DATE].dt.date
        else:
            new_column = self._df[field]

        self._current[field] = new_column
        return self

    def group_by(self, aggregation: GroupBy, field=None):
        """
        Group by a field and aggregate with the specified operation.
        By default, groups by the oldest field and sorts in ascending order of group.
        """
        if field:
            rest = self._current.columns != field
        else:
            # Destructure columns
            field, *rest = self._current

        grouped = self._current.groupby(field)[rest]
        self._current = aggregation(grouped).reset_index()

        # Add metadata
        for grouped_field in rest:
            self._metadata.set_group_by(grouped_field, aggregation)
        return self

    def value_counts(self):
        """
        Special case of group-by: value counts of a single field.
        By default, sorts in ascending order of count.
        """
        (field,) = self._current
        counts = self._current[field].value_counts()
        self._current = counts.reset_index()
        return self

    def sort(self, field: Field, ascending: bool = True):
        self._current = self._current.sort_values(by=field, ascending=ascending)
        return self

    def filter(self, field: Field, condition, description):
        """
        Apply a filter to the DataFrame via a condition.
        `condition` is a lambda function or callable that takes the column values and returns a boolean mask.
        """
        self._current = self._current[condition(self._current[field])]
        self._metadata.add_filter(field, description)
        return self

    @property
    def dataframe(self) -> pd.DataFrame:
        """
        Return the current DataFrame state.
        """
        return self._current

    @property
    def metadata(self) -> Metadata:
        """
        Return the current DataFrame metadata.
        """
        return self._metadata

    def reset(self):
        """
        Reset current state.
        """
        self._current = pd.DataFrame()
        self._metadata = Metadata()
