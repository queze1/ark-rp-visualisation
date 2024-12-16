from enum import Enum, StrEnum, auto

import plotly.express as px


class FieldType(Enum):
    NUMERICAL = auto()
    CATEGORICAL = auto()
    TEMPORAl = auto()


class Field(StrEnum):
    AUTHOR = "author"
    DATE = "date"
    HOUR = "hour"
    DAY = "day"
    # Only used internally for querying
    REACTIONS = "reactions"
    REACTION_COUNT = "reaction_count"
    WORD_COUNT = "word_count"
    CHANNEL_NAME = "channel_name"
    SCENE_END = "scene_end"
    COUNT = "count"

    @property
    def _metadata(self):
        return {
            "AUTHOR": {"description": "Users", FieldType.CATEGORICAL: True},
            "DATE": {
                "description": "Day",
                "label": "Date",
                FieldType.TEMPORAl: True,
                FieldType.CATEGORICAL: True,
            },
            "HOUR": {
                "description": "Hour of Day",
                FieldType.TEMPORAl: True,
                FieldType.CATEGORICAL: True,
            },
            "DAY": {
                "description": "Day of Month",
                FieldType.TEMPORAl: True,
                FieldType.CATEGORICAL: True,
            },
            "REACTION_COUNT": {
                "description": "Number of Reactions",
                "label": "Reactions",
                FieldType.NUMERICAL: True,
            },
            "WORD_COUNT": {
                "description": "Word Count",
                "label": "Words",
                FieldType.NUMERICAL: True,
            },
            "CHANNEL_NAME": {
                "description": "Channels",
                FieldType.CATEGORICAL: True,
            },
            "SCENE_END": {
                "description": "Scene Ends",
                "label": "Scenes",
                FieldType.NUMERICAL: True,
            },
            "COUNT": {
                "description": "Messages",
                FieldType.NUMERICAL: True,
            },
        }

    @property
    def description(self):
        return self._metadata[self.name]["description"]

    @property
    def label(self):
        # Label defaults to description
        return self._metadata[self.name].get("label", self.description)

    @property
    def numerical(self):
        return self._metadata[self.name].get(FieldType.NUMERICAL, False)

    @property
    def categorical(self):
        return self._metadata[self.name].get(FieldType.CATEGORICAL, False)

    @property
    def temporal(self):
        return self._metadata[self.name].get(FieldType.TEMPORAl, False)


class GroupBy(StrEnum):
    SUM = "sum"
    MEAN = "mean"
    NUNIQUE = "nunique"

    def __call__(self, obj):
        if self is GroupBy.SUM:
            return obj.sum()
        elif self is GroupBy.MEAN:
            return obj.mean()
        elif self is GroupBy.NUNIQUE:
            return obj.nunique()
        raise NotImplementedError(f"{self.value} groupby is not implemented.")

    @property
    def _metadata(self):
        return {
            "SUM": {"label_prefix": "Number of "},
            "MEAN": {
                "description_prefix": "Average ",
                "label_prefix": "Avg. ",
            },
            "NUNIQUE": {
                "description_prefix": "Unique ",
                "label_prefix": "Unique ",
            },
        }

    @property
    def description_prefix(self):
        return self._metadata[self.name].get("description_prefix", "")

    @property
    def label_prefix(self):
        # Label defaults to description
        return self._metadata[self.name].get("label_prefix", "")


class Plot(StrEnum):
    BAR = "bar"
    SCATTER = "scatter"
    LINE = "line"

    def __call__(self, *args, **kwargs):
        if self is Plot.BAR:
            return px.bar(*args, **kwargs)
        elif self is Plot.SCATTER:
            return px.scatter(*args, **kwargs)
        elif self is Plot.LINE:
            return px.line(*args, **kwargs)
        raise NotImplementedError(f"{self.value} plot is not implemented.")


class Filter(StrEnum):
    MIN = "min"
    MAX = "max"
    EQUAL = "equal"

    def __call__(self, field, value):
        if self is Filter.MIN:
            return value <= field
        if self is Filter.MAX:
            return field <= value
        if self is Filter.EQUAL:
            return field == value

    @property
    def symbol(self):
        return {
            "MIN": "≥",
            "MAX": "≤",
            "EQUAL": "=",
        }[self.name]
