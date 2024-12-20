from enum import Enum, StrEnum, auto

import plotly.express as px


class FieldType(Enum):
    NUMERICAL = auto()
    CATEGORICAL = auto()
    TEMPORAl = auto()


class Field(StrEnum):
    AUTHOR = "author"
    CHANNEL_NAME = "channel_name"
    COUNT = "count"
    DATE = "date"
    DAY = "day"
    HOUR = "hour"
    REACTION_COUNT = "reaction_count"
    SCENE_END = "scene_end"
    WORD_COUNT = "word_count"

    # Internal use only
    REACTIONS = "reactions"

    @property
    def _metadata(self):
        return {
            "AUTHOR": {"description": "Users", FieldType.CATEGORICAL: True},
            "DATE": {
                "description": "Date",
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
                "description": "Reactions",
                "label": "Reaction Count",
                FieldType.NUMERICAL: True,
            },
            "WORD_COUNT": {
                "description": "Words",
                "label": "Word Count",
                FieldType.NUMERICAL: True,
            },
            "CHANNEL_NAME": {
                "description": "Channels",
                FieldType.CATEGORICAL: True,
            },
            "SCENE_END": {
                "description": "Scene Ends",
                FieldType.NUMERICAL: True,
            },
            "COUNT": {
                "description": "Messages",
                FieldType.NUMERICAL: True,
            },
        }.get(self.name, {})

    @property
    def description(self):
        return self._metadata.get("description")

    @property
    def label(self):
        # Label defaults to description
        return self._metadata.get("label", self.description)

    @property
    def numerical(self):
        return self._metadata.get(FieldType.NUMERICAL, False)

    @property
    def categorical(self):
        return self._metadata.get(FieldType.CATEGORICAL, False)

    @property
    def temporal(self):
        return self._metadata.get(FieldType.TEMPORAl, False)


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
        raise NotImplementedError(f"{self.name} groupby is not implemented.")


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
        raise NotImplementedError(f"{self.name} plot is not implemented.")


class Operator(StrEnum):
    LT = "<"
    LEQ = "<="
    GT = ">"
    GEQ = ">="
    EQ = "="

    def __call__(self, series, value):
        if self is Operator.LT:
            return value < series
        elif self is Operator.LEQ:
            return series <= value
        elif self is Operator.GT:
            return series > value
        elif self is Operator.GEQ:
            return series >= value
        elif self is Operator.EQ:
            return series == value
        raise NotImplementedError(f"{self.name} operator is not implemented.")


class MatchOperator(StrEnum):
    IS = "is"
    IS_NOT = "is not"

    def __call__(self, series, values):
        if self is MatchOperator.IS:
            return series.isin(values)
        elif self is MatchOperator.IS_NOT:
            return ~series.isin(values)
        raise NotImplementedError(f"{self.name} operator is not implemented.")


class DateOperator(StrEnum):
    BEFORE = "before"
    DURING = "during"
    AFTER = "after"

    def __call__(self, series, value):
        if self is DateOperator.BEFORE:
            return value < series
        elif self is DateOperator.DURING:
            return series == value
        elif self is Operator.AFTER:
            return series > value
        raise NotImplementedError(f"{self.name} operator is not implemented.")
