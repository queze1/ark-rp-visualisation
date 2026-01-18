from dataclasses import dataclass
from dataclasses import field as data_field
from typing import Any, Optional

import pandas as pd

from enums import Field, Filter, GroupBy, Operator, Text


def _add_derived_field(df: pd.DataFrame, field: Field) -> pd.DataFrame:
    """Add a derived field to the DataFrame if it doesn't exist."""
    if field not in df.columns:
        if field == Field.HOUR:
            df[field] = df[Field.DATETIME].dt.hour
        elif field == Field.DAY:
            df[field] = df[Field.DATETIME].dt.day
        elif field == Field.DATE:
            df[field] = df[Field.DATETIME].dt.date
        elif field == Field.COUNT:
            df[field] = 1
    return df


@dataclass
class AxisConfig:
    fields: list[Field]
    aggregations: dict[Field, GroupBy]
    x_axis: Field
    y_axis: Field

    @classmethod
    def from_raw(
        cls,
        selected_fields: list[str],
        selected_axes: list[str],
        selected_aggregations: list[str],
    ):
        fields = [Field(field) for field in selected_fields]
        primary_field, secondary_field, *_ = fields
        aggregations = {
            field: GroupBy(agg) for field, agg in zip(fields, selected_aggregations)
        }

        # Find field axes
        if selected_axes == [Text.Y_AXIS, Text.X_AXIS]:
            axes = dict(y_axis=primary_field, x_axis=secondary_field)
        elif selected_axes == [Text.X_AXIS, Text.Y_AXIS]:
            axes = dict(x_axis=primary_field, y_axis=secondary_field)
        else:
            raise ValueError("Invalid axes")
        return cls(fields=fields, aggregations=aggregations, **axes)

    def get_label(
        self, field: Field, figure_config: "FigureConfig", label_type: str = "axis"
    ) -> str:
        """
        Determine the label for a field by checking overrides,
        aggregations, and metadata.
        """
        # 1. Check for manual overrides from the Customisation tab
        if field == self.x_axis and figure_config.x_label:
            return figure_config.x_label
        if field == self.y_axis and figure_config.y_label:
            return figure_config.y_label

        # 2. Get the base label from the Field enum
        base_label = field.axis_label if label_type == "axis" else field.title_label

        # 3. Prepend aggregation prefixes if an aggregation is active for this field
        if field in self.aggregations:
            agg = self.aggregations[field]
            prefix = agg.axis_prefix if label_type == "axis" else agg.title_prefix
            return f"{prefix}{base_label}"

        return base_label

    def prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure all fields required for axes exist in the df."""
        for field in self.fields:
            df = _add_derived_field(df, field)
        return df


@dataclass
class FilterGroup:
    field: Field
    operator: Operator
    value: Any

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return df[self.operator(df[self.field], self.value)]


@dataclass
class FilterConfig:
    filters: list[FilterGroup]

    @classmethod
    def from_raw(
        cls,
        filter_types: list[Field],
        filter_operators: list[str],
        filter_values: list[Any],
    ):
        filters = [
            FilterGroup(
                field=Field(filter_type),
                operator=Operator(operator),
                value=Filter(filter_type).post_processing(value),
            )
            for filter_type, operator, value in zip(
                filter_types, filter_operators, filter_values
            )
            if value
        ]
        return cls(filters)

    def prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure all fields required for filtering exist in the df."""
        for filter_group in self.filters:
            df = _add_derived_field(df, filter_group.field)
        return df

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all filter groups to the dataframe."""
        for f in self.filters:
            df = f.apply(df)
        return df


@dataclass
class SortConfig:
    ascending: bool
    axis: str

    @classmethod
    def from_raw(cls, order: str, axis: str):
        return cls(
            ascending=order == Text.ASCENDING,
            axis=axis,
        )


@dataclass
class FigureConfig:
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    x_log: bool = False
    y_log: bool = False
    moving_averages: list[int] = data_field(default_factory=list)
    sort: Optional[SortConfig] = None

    @classmethod
    def from_raw(
        cls,
        title: str,
        x_label: str,
        y_label: str,
        x_log: bool,
        y_log: bool,
        moving_averages: dict[int, bool],
        sort_order: str,
        sort_axis: str,
    ):
        return cls(
            title=title,
            x_label=x_label,
            y_label=y_label,
            x_log=x_log,
            y_log=y_log,
            moving_averages=[
                int(window) for window, enabled in moving_averages.items() if enabled
            ],
            sort=SortConfig.from_raw(sort_order, sort_axis)
            if sort_order and sort_axis
            else None,
        )
