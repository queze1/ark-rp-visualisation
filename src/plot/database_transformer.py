import pandas as pd

from .enums import Field, GroupBy


class DatabaseTransformer:
    def __init__(self, df: pd.DataFrame):
        self._df = df
        # Initialise current state as empty
        self._current = pd.DataFrame()
        # Track the pipeline of what was applied
        self._history = []

    def _log_operation(self, operation: str, details: dict):
        """
        Log details of operations for serialization into labels or titles.
        """
        self._history.append({"operation": operation, **details})

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

        self._log_operation("add_field", {"field": field})
        return self

    def group_by(self, operation: GroupBy):
        """
        Group by the oldest field and aggregate with the specified operation.
        By default, sorts in ascending order of group.
        """
        field, *rest = self._current
        grouped = self._current.groupby(field)[rest]
        self._current = operation(grouped).reset_index()

        self._log_operation(
            "group_by",
            {
                "field": field,
                "operation": operation.value,
            },
        )
        return self

    def value_counts(self):
        """
        Special case of group-by: value counts of a single field.
        By default, sorts in ascending order of count.
        """
        (field,) = self._current
        counts = self._current[field].value_counts()
        self._current = counts.reset_index()

        self._log_operation("value_counts", {"field": field})
        return self

    def sort(self, field: Field, ascending: bool = True):
        self._current = self._current.sort_values(by=field, ascending=ascending)

        direction = "ascending" if ascending else "descending"
        self._log_operation("sort", {"field": field, "order": direction})
        return self

    def get_dataframe(self) -> pd.DataFrame:
        """
        Retrieve the current DataFrame state.
        """
        return self._current

    def get_history(self) -> list:
        """
        Retrieve the transformation history for labels and titles.
        """
        return self._history

    def reset(self):
        """
        Reset history and current state.
        """
        self._current = pd.DataFrame()
        self._history = []
