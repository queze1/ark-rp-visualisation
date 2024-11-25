import pandas as pd
from .enums import Field, GroupBy


field_metadata = {
    Field.AUTHOR_ID: {
        "description": "User",
        "label": "User",
        "needs_plural": True,
    },
    Field.AUTHOR: {
        "description": "User",
        "label": "User",
        "needs_plural": True,
    },
    Field.DATE: {"description": "Day", "label": "Date"},
    Field.HOUR: {"description": "Hour of Day", "label": "Hour of Day"},
    Field.DAY: {"description": "Day of Month", "label": "Day of Month"},
    Field.CONTENT: {"description": "Messages", "label": "Number of Messages"},
    Field.ATTACHMENTS: {"description": "Attachments", "label": "Attachments"},
    Field.REACTIONS: {"description": "Reactions", "label": "Reactions"},
    Field.REACTION_COUNT: {
        "description": "Reactions",
        "label": "Reactions",
    },
    Field.WORD_COUNT: {"description": "Words", "label": "Words"},
    Field.CHANNEL_NAME: {"description": "Channels", "label": "Channels"},
    Field.SCENE_ID: {"description": "Scenes", "label": "Scenes"},
    Field.COUNT: {"description": "Messages", "label": "Number of Messages"},
}

group_by_metadata = {
    GroupBy.SUM: lambda x: {
        "description": f"{x['description']}",
        "label": f"Number of {x['label']}",
    },
    GroupBy.MEAN: lambda x: {
        "description": f"Average {x['description']}",
        "label": f"Average {x['label']}",
    },
    GroupBy.NUNIQUE: lambda x: {
        "description": f"Unique {x['description']}",
        "label": f"Unique {x['label']}",
    },
}


class DatabaseTransformer:
    def __init__(self, df: pd.DataFrame):
        self._df = df
        self._current = pd.DataFrame()
        self._metadata = {}

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

        # Plurals for Y-axis
        needs_plural = (
            field_metadata[field].get("needs_plural")
            # Check if current index position corresponds to Y-axis
            and self._current.columns.get_loc(field) != 0
        )
        if needs_plural:
            # Add "s" to the end
            self._metadata[field] = {
                "description": field_metadata[field]["description"] + "s",
                "label": field_metadata[field]["label"] + "s",
            }
        else:
            self._metadata[field] = field_metadata[field]
        return self

    def group_by(self, operation: GroupBy):
        """
        Group by the oldest field and aggregate with the specified operation.
        By default, sorts in ascending order of group.
        """
        field, *rest = self._current
        grouped = self._current.groupby(field)[rest]
        self._current = operation(grouped).reset_index()

        # Add metadata
        for grouped_field in rest:
            self._metadata[grouped_field] = group_by_metadata[operation](
                self._metadata[grouped_field]
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

        # Add metadata
        self._metadata[Field.COUNT] = field_metadata[Field.COUNT]
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

    @property
    def metadata(self) -> dict:
        """
        Return the current DataFrame metadata.
        """
        return self._metadata

    def reset(self):
        """
        Reset current state.
        """
        self._current = pd.DataFrame()
