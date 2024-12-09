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
    SCENE_ID = "sceneId"
    COUNT = "count"


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
