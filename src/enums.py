from enum import Enum, StrEnum, auto

import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px


class FieldType(Enum):
    NUMERICAL = auto()
    CATEGORICAL = auto()
    TEMPORAl = auto()


class GroupBy(StrEnum):
    SUM = "sum"
    MEAN = "mean"
    NUNIQUE = "nunique"

    @property
    def _metadata(self):
        return {
            "SUM": {"label": "Total", "axis_prefix": "Number of "},
            "MEAN": {
                "label": "Average",
                "title_prefix": "Average ",
                "axis_prefix": "Avg. ",
            },
            "NUNIQUE": {
                "label": "Unique",
                "title_prefix": "Unique ",
                "axis_prefix": "Unique ",
            },
        }

    @property
    def label(self):
        return self._metadata[self.name].get("label", self.value)

    @property
    def title_prefix(self):
        return self._metadata[self.name].get("title_prefix", "")

    @property
    def axis_prefix(self):
        return self._metadata[self.name].get("axis_prefix", "")


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
    AUTHOR_ID = "author_id"
    ATTACHMENTS = "attachments"
    CONTENT = "content"
    DATETIME = "datetime"
    REACTIONS = "reactions"

    @property
    def _metadata(self):
        return {
            "AUTHOR": {
                "axis_label": "Users",
                "categorical": True,
                "aggregations": [GroupBy.NUNIQUE],
            },
            "DATE": {
                "axis_label": "Date",
                "temporal": True,
                "categorical": True,
                "aggregations": [GroupBy.NUNIQUE],
            },
            "HOUR": {
                "axis_label": "Hour of Day",
                "temporal": True,
                "categorical": True,
                "aggregations": [GroupBy.NUNIQUE],
            },
            "DAY": {
                "axis_label": "Day of Month",
                "temporal": True,
                "categorical": True,
                "aggregations": [GroupBy.NUNIQUE],
            },
            "REACTION_COUNT": {
                "axis_label": "Reactions",
                "label": "Reaction Count",
                "numerical": True,
                "aggregations": [GroupBy.SUM, GroupBy.MEAN],
            },
            "WORD_COUNT": {
                "axis_label": "Words",
                "label": "Word Count",
                "numerical": True,
                "aggregations": [GroupBy.SUM, GroupBy.MEAN],
            },
            "CHANNEL_NAME": {
                "axis_label": "Channels",
                "categorical": True,
                "aggregations": [GroupBy.NUNIQUE],
            },
            "SCENE_END": {
                "axis_label": "Scene Ends",
                "numerical": True,
                "aggregations": [GroupBy.SUM],
            },
            "COUNT": {
                "axis_label": "Messages",
                "numerical": True,
                "aggregations": [GroupBy.SUM],
            },
        }.get(self.name, {})

    @property
    def axis_label(self):
        return self._metadata.get("axis_label")

    @property
    def title_label(self):
        # Title label defaults to axis label
        return self._metadata.get("title_label", self.axis_label)

    @property
    def label(self):
        # Label defaults to axis label
        return self._metadata.get("label", self.axis_label)

    @property
    def numerical(self):
        return self._metadata.get("numerical", False)

    @property
    def categorical(self):
        return self._metadata.get("categorical", False)

    @property
    def temporal(self):
        return self._metadata.get("temporal", False)

    @property
    def aggregations(self):
        return self._metadata.get("aggregations", [])


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
            return series < value
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
                "fields": [
                    {
                        "allowed": non_temporal_fields,
                    },
                    {
                        "allowed": [Field.DATE],
                        "default": Field.DATE,
                    },
                ],
            },
            "BAR": {
                "label": "Bar",
                "plot_type": Plot.BAR,
                "fields": [
                    {
                        "allowed": fields_with_label,
                    },
                    {
                        "allowed": groupable_fields,
                    },
                ],
            },
            "SCATTER": {
                "label": "Scatter (2 vars)",
                "plot_type": Plot.SCATTER,
                "fields": [
                    {
                        "allowed": fields_with_label,
                    },
                    {
                        "allowed": groupable_fields,
                    },
                ],
            },
            "SCATTER_2": {
                "label": "Scatter (3 vars)",
                "plot_type": Plot.SCATTER,
                "fields": [
                    {
                        "allowed": fields_with_label,
                    },
                    {
                        "allowed": fields_with_label,
                    },
                    {
                        "allowed": groupable_fields,
                    },
                ],
            },
        }.get(self.name, {})

    @property
    def label(self):
        return self._metadata.get("label")

    @property
    def plot_type(self):
        return self._metadata.get("plot_type")

    @property
    def fields(self):
        return self._metadata.get("fields")


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
                "default_operator": Operator.BEFORE,
                "select_input": dmc.DatePickerInput,
                "select_kwargs": dict(
                    clearable=True,
                    placeholder="Enter date...",
                ),
                "post_processing": lambda value: pd.to_datetime(value).date(),
            },
            "AUTHOR": {
                "label": "Author",
                "operators": [Operator.IN, Operator.NOT_IN],
                "default_operator": Operator.IN,
                "select_input": dmc.MultiSelect,
                "select_kwargs": multiselect_kwargs,
            },
            "CHANNEL_NAME": {
                "label": "Channel Name",
                "operators": [Operator.IN, Operator.NOT_IN],
                "default_operator": Operator.IN,
                "select_input": dmc.MultiSelect,
                "select_kwargs": multiselect_kwargs,
            },
            "HOUR": {
                "label": "Hour",
                "operators": standard_operators,
                "default_operator": Operator.GEQ,
                "select_input": dmc.Select,
                "select_kwargs": dict(
                    data=[str(hour) for hour in range(24)],
                    placeholder="Enter hour...",
                    searchable=True,
                    clearable=True,
                ),
                "post_processing": int,
            },
            "REACTION_COUNT": {
                "label": "Reaction Count",
                "operators": standard_operators,
                "default_operator": Operator.GEQ,
                "select_input": dmc.NumberInput,
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
    def select_input(self):
        return self._metadata.get("select_input")

    @property
    def select_kwargs(self):
        return self._metadata.get("select_kwargs", {})

    @property
    def post_processing(self):
        # Default is to return value unchanged
        return self._metadata.get("post_processing", lambda value: value)


class Text(StrEnum):
    TITLE = "ARK RP Visualisation"
    EXPLAINER = "For the 2024 ARK: Journey Through the Realms campaign, not endorsed by the UNSW Tabletop Games Society."
    PLOT = "Plot"
    BY = "By"
    AND = "And"
    Y_AXIS = "Y-Axis"
    X_AXIS = "X-Axis"
    ASCENDING = "ascending"
    DESCENDING = "descending"
    UPDATE_GRAPH_LABEL = "This is how I like it!"


class Page(StrEnum):
    GRAPH = "graph"
    UPDATE_GRAPH_BUTTON = "update-graph-btn"

    FIELD_CONTAINER = "field-container"
    FIELD_DROPDOWN = "field-dropdown"
    FIELD_AGG_CONTAINER = "field-agg-container"
    FIELD_AGG_DROPDOWN = "field-agg-dropdown"
    FIELD_AGG_SPACING = "axis-container"
    FIELD_SPACING = "field-spacing"
    AXIS_TEXT = "axis-text"
    SWAP_AXES_BUTTON = "swap-axis-btn"

    FILTER_CONTAINER = "filter-container"
    FILTER_GROUP_CONTAINER = "filter-group-container"
    RESET_FILTER_BUTTON = "reset-filter-btn"
    ADD_FILTER_BUTTON = "add-filter-btn"
    DELETE_FILTER_BUTTON = "delete-filter-btn"
    FILTER_TYPE = "filter-type"
    FILTER_OPERATOR = "filter-operator"
    FILTER_VALUE_CONTAINER = "filter-value-container"
    FILTER_VALUE = "filter-value"

    RESET_CUSTOMISATION_BUTTON = "reset-customisation-btn"
    TITLE_INPUT = "title-input"
    X_LABEL_INPUT = "x-label-input"
    Y_LABEL_INPUT = "y-label-input"
    X_LOG_CHECKBOX = "x-log-checkbox"
    Y_LOG_CHECKBOX = "y-log-checkbox"
    MOVING_AVERAGE_7 = "moving-average-7"
    MOVING_AVERAGE_30 = "moving-average-30"
    SORT_ORDER_DROPDOWN = "sort-order-dropdown"
    SORT_AXIS_DROPDOWN = "sort-axis-dropdown"
