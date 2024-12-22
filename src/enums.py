from enum import Enum, StrEnum, auto

import plotly.express as px
import dash_mantine_components as dmc


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
    IN = "in"
    NOT_IN = "not in"

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
        elif self is Operator.IN:
            return series.isin(value)
        elif self is Operator.NOT_IN:
            return ~series.isin(value)
        raise NotImplementedError(f"{self.name} operator is not implemented.")


class Tab(StrEnum):
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    SCATTER_2 = "scatter2"

    @property
    def _metadata(self):
        fields_with_label = [field for field in Field if field.label]
        non_temporal_fields = [
            field for field in fields_with_label if not field.temporal
        ]
        # Cannot group by COUNT because it's trivial, cannot group by SCENE_END because it's a boolean
        groupable_fields = [
            field
            for field in fields_with_label
            if field not in {Field.COUNT, Field.SCENE_END}
        ]

        return {
            "LINE": {
                "label": "Time Series",
                "plot_type": Plot.LINE,
                "primary_field": {
                    "allowed": non_temporal_fields,
                },
                "secondary_field": {"allowed": [Field.DATE], "default": Field.DATE},
            },
            "BAR": {
                "label": "Bar",
                "plot_type": Plot.BAR,
                "primary_field": {
                    "allowed": fields_with_label,
                },
                "secondary_field": {
                    "allowed": groupable_fields,
                },
            },
            "SCATTER": {
                "label": "Scatter (2 vars)",
                "plot_type": Plot.SCATTER,
                "primary_field": {
                    "allowed": fields_with_label,
                },
                "secondary_field": {
                    "allowed": groupable_fields,
                },
            },
            "SCATTER_2": {
                "label": "Scatter (3 vars)",
                "plot_type": Plot.SCATTER,
                "primary_field": {
                    "allowed": fields_with_label,
                },
                "secondary_field": {
                    "allowed": fields_with_label,
                },
                "tertiary_field": {
                    "allowed": groupable_fields,
                },
            },
        }.get(self.name, {})

    @property
    def label(self):
        return self._metadata.get("label")

    @property
    def plot_type(self):
        return self._metadata.get("plot_type")

    @property
    def primary_field(self):
        return self._metadata.get("primary_field")

    @property
    def secondary_field(self):
        return self._metadata.get("secondary_field")

    @property
    def tertiary_field(self):
        return self._metadata.get("tertiary_field")


class Text(StrEnum):
    TITLE = "ARK Data Visualisation"
    EXPLAINER = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""
    PLOT = "Plot"
    BY = "By"
    AND = "And"
    Y_AXIS = "Y-Axis"
    X_AXIS = "X-Axis"
    UPDATE_GRAPH_LABEL = "This is how I like it!"


class Page(StrEnum):
    GRAPH = "graph"
    FIELD_DROPDOWN = "field-dropdown"
    UPDATE_GRAPH_BUTTON = "update-graph-btn"
    AXIS_TEXT = "axis-text"
    SWAP_AXES_BUTTON = "swap-axis-btn"
    RESET_FILTER_BUTTON = "reset-filter-btn"
    FILTER_OPERATOR = "filter-operator"
    FILTER_VALUE = "filter-value"


class FilterOption(Enum):
    # Means replace this with the unique values of this field
    FIELD_UNIQUE = auto()


class Filter(StrEnum):
    DATE = Field.DATE.value
    AUTHOR = Field.AUTHOR.value
    CHANNEL_NAME = Field.CHANNEL_NAME.value
    HOUR = Field.HOUR.value
    REACTION_COUNT = Field.REACTION_COUNT.value

    @property
    def _metadata(self):
        standard_operators = [
            Operator.LT,
            Operator.LEQ,
            Operator.GT,
            Operator.GEQ,
            Operator.EQ,
        ]
        multiselect_kwargs = dict(
            data=FilterOption.FIELD_UNIQUE,
            placeholder="Select...",
            searchable=True,
            clearable=True,
        )

        return {
            "DATE": {
                "label": "Date",
                "operators": [Operator.BEFORE, Operator.DURING, Operator.AFTER],
                "default_operator": Operator.DURING,
                "select_component": dmc.DatePickerInput,
                "select_kwargs": dict(
                    clearable=True,
                ),
            },
            "AUTHOR": {
                "label": "Author",
                "operators": [Operator.IN, Operator.NOT_IN],
                "default_operator": Operator.IN,
                "select_component": dmc.MultiSelect,
                "select_kwargs": multiselect_kwargs,
            },
            "CHANNEL_NAME": {
                "label": "Channel Name",
                "operators": [Operator.IN, Operator.NOT_IN],
                "default_operator": Operator.IN,
                "select_component": dmc.MultiSelect,
                "select_kwargs": multiselect_kwargs,
            },
            "HOUR": {
                "label": "Hour",
                "operators": standard_operators,
                "default_operator": Operator.GEQ,
                "select_component": dmc.Select,
                "select_kwargs": dict(
                    data=[str(hour) for hour in range(24)],
                    placeholder="Enter hour...",
                    searchable=True,
                    clearable=True,
                ),
            },
            "REACTION_COUNT": {
                "label": "Reaction Count",
                "operators": standard_operators,
                "default_operator": Operator.GEQ,
                "select_component": dmc.NumberInput,
                "select_kwargs": dict(
                    min=0,
                    max=99,
                    allowDecimal=False,
                    placeholder="Enter number...",
                ),
            },
        }.get(self.name, {})

    @property
    def label(self):
        return self._metadata.get("label")

    @property
    def operators(self):
        return self._metadata.get("operators")

    @property
    def default_operator(self):
        return self._metadata.get("default_operator")

    @property
    def select_component(self):
        return self._metadata.get("select_component")

    @property
    def select_kwargs(self):
        return self._metadata.get("select_kwargs", {})