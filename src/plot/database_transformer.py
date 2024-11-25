import pandas as pd

from .enums import Field, GroupBy


class DatabaseTransformer:
    def __init__(self, df: pd.DataFrame):
        self._df = df
        self._current = pd.DataFrame()

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

    def group_by(self, operation: GroupBy):
        """
        Group by the oldest field and aggregate with the specified operation.
        By default, sorts in ascending order of group.
        """
        field, *rest = self._current
        grouped = self._current.groupby(field)[rest]
        self._current = operation(grouped).reset_index()
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

    @property
    def dataframe(self) -> pd.DataFrame:
        """
        Return the current DataFrame state.
        """
        return self._current

    def reset(self):
        """
        Reset current state.
        """
        self._current = pd.DataFrame()
