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
    # Inequalities
    LT = "<"
    LEQ = "<="
    GT = ">"
    GEQ = ">="
    EQ = "="

    # Inequality aliases
    BEFORE = "before"
    DURING = "during"
    AFTER = "after"

    # Inclusion
    IS = "is"
    IS_NOT = "is not"

    def __call__(self, series, value):
        if self in {Operator.LT, Operator.BEFORE}:
            return value < series
        elif self is Operator.LEQ:
            return series <= value
        elif self in {Operator.GT, Operator.AFTER}:
            return series > value
        elif self is Operator.GEQ:
            return series >= value
        elif self in {Operator.EQ, Operator.DURING}:
            return series == value
        elif self is Operator.IS:
            return series.isin(value)
        elif self is Operator.IS_NOT:
            return ~series.isin(value)
        raise NotImplementedError(f"{self.name} operator is not implemented.")


class Tab(StrEnum):
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"

    @property
    def _metadata(self):
        fields_with_label = [field for field in Field if field.label]
        non_temporal_fields = [
            field for field in fields_with_label if not field.temporal
        ]

        return {
            "LINE": {
                "label": "Time Series",
                "primary_field": {
                    "allowed": non_temporal_fields,
                },
                "secondary_field": {"allowed": [Field.DATE], "default": Field.DATE},
            },
            "BAR": {
                "label": "Bar",
                "primary_field": {
                    "allowed": fields_with_label,
                },
                "secondary_field": {
                    "allowed": fields_with_label,
                },
            },
            "SCATTER": {
                "label": "Scatter",
                "primary_field": {
                    "allowed": fields_with_label,
                },
                "secondary_field": {
                    "allowed": fields_with_label,
                },
            },
        }.get(self.name, {})

    @property
    def label(self):
        return self._metadata.get("label")

    @property
    def primary_field(self):
        return self._metadata.get("primary_field")

    @property
    def secondary_field(self):
        return self._metadata.get("secondary_field")


class Text(StrEnum):
    TITLE = "ARK Data Visualisation"
    EXPLAINER = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""


class Page(StrEnum):
    TABS = "tabs"
    GRAPH = "graph"
    FIELD_DROPDOWN = "field-dropdown"
    SUBMIT_BUTTON = "submit-button"

    def __call__(self, tab):
        if self in {Page.FIELD_DROPDOWN, Page.SUBMIT_BUTTON, Page.GRAPH}:
            return f"{tab}-{self.value}"
