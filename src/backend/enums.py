from enum import StrEnum

import plotly.express as px


class Field(StrEnum):
    AUTHOR = "author"
    DATE = "date"
    HOUR = "hour"
    DAY = "day"
    REACTIONS = "reactions"
    REACTION_COUNT = "reaction_count"
    WORD_COUNT = "word_count"
    CHANNEL_NAME = "channel_name"
    SCENE_ID = "scene_id"
    COUNT = "count"

    @property
    def _metadata(self):
        return {
            "AUTHOR": {
                "description": "Users",
            },
            "DATE": {
                "description": "Day",
                "label": "Date",
            },
            "HOUR": {"description": "Hour of Day"},
            "DAY": {"description": "Day of Month"},
            "REACTIONS": {"description": "Reactions"},
            "REACTION_COUNT": {
                "description": "Number of Reactions",
                "label": "Reactions",
            },
            "WORD_COUNT": {
                "description": "Word Count",
                "label": "Words",
            },
            "CHANNEL_NAME": {"description": "Channels"},
            "SCENE_ID": {"description": "Scenes"},
            "COUNT": {"description": "Messages"},
        }

    @property
    def description(self):
        return self._metadata[self.name]["description"]

    @property
    def label(self):
        # Label defaults to description
        return self._metadata[self.name].get("label", self.description)


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
