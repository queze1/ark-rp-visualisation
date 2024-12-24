from dataclasses import dataclass, field as data_field
from operator import attrgetter

import pandas as pd

from data_loader import df
from enums import Field, Filter, GroupBy, Operator, Plot, Text


@dataclass
class AxisConfig:
    fields: list[Field]
    x_axis: Field
    y_axis: Field

    @classmethod
    def from_raw(cls, selected_fields: list[str], selected_axes: list[str]):
        selected_fields = [Field(field) for field in selected_fields]
        primary_field, secondary_field, *_ = selected_fields

        # Find field axes
        if selected_axes == [Text.Y_AXIS, Text.X_AXIS]:
            axes = dict(y_axis=primary_field, x_axis=secondary_field)
        elif selected_axes == [Text.X_AXIS, Text.Y_AXIS]:
            axes = dict(x_axis=primary_field, y_axis=secondary_field)
        else:
            raise ValueError("Invalid axes")
        return cls(fields=selected_fields, **axes)


@dataclass
class FilterGroup:
    field: str
    operator: Operator
    value: object

    @classmethod
    def from_raw(cls, type: str, operator: str, value: object):
        return cls(
            field=type,
            operator=Operator(operator),
            value=Filter(type).post_processing(value),
        )

    def apply(self, df: pd.DataFrame):
        return df[self.operator(df[self.field], self.value)]


@dataclass
class FilterConfig:
    filters: list[FilterGroup]

    @classmethod
    def from_raw(cls, filters):
        return cls(
            filters=[
                FilterGroup.from_raw(type, operator, value)
                for type, operator, value in zip(*filters)
                if value
            ]
        )


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
    title: str = None
    x_label: str = None
    y_label: str = None
    x_log: bool = False
    y_log: bool = False
    moving_averages: list = data_field(default_factory=[])
    sort: SortConfig = None

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
                window for window, enabled in moving_averages.items() if enabled
            ],
            sort=SortConfig.from_raw(sort_order, sort_axis)
            if sort_order and sort_axis
            else None,
        )


class PlotBuilder:
    def __init__(
        self,
        plot_type: Plot,
        axis_config: AxisConfig,
        filter_config: FilterConfig,
        figure_config: FigureConfig,
    ):
        self._df = df.copy()
        self._fig = None
        self._grouping_field = None
        self._grouped_fields = None
        self._aggregations = None

        self.fields, self.x_axis, self.y_axis = attrgetter(
            "fields", "x_axis", "y_axis"
        )(axis_config)
        self.filters = filter_config.filters
        self.plot_type = plot_type

        (
            self.title,
            self.x_label,
            self.y_label,
            self.x_log,
            self.y_log,
            self.moving_averages,
            self.sort,
        ) = attrgetter(
            "title", "x_label", "y_label", "x_log", "y_log", "moving_averages", "sort"
        )(figure_config)

    def add_field(self, field: Field):
        # Create the field if it doesn't already exist
        if field in self._df:
            return

        if field == Field.HOUR:
            self._df[field] = self._df[Field.DATETIME].dt.hour
        elif field == Field.DAY:
            self._df[field] = self._df[Field.DATETIME].dt.day
        elif field == Field.DATE:
            self._df[field] = self._df[Field.DATETIME].dt.date
        elif field == Field.COUNT:
            self._df[field] = 1

    def add_fields(self):
        for field in self.fields:
            self.add_field(field)

    def apply_filters(self):
        for filter in self.filters:
            self.add_field(filter.field)
            self._df = filter.apply(self._df)

    def set_aggregations(self, aggregations: dict[Field, GroupBy] = {}):
        """Sets aggregations, if not provided, uses default aggregations."""
        if aggregations:
            self._grouped_fields = aggregations.keys()
            # Find the one field which is not aggregated
            (self._grouping_field,) = [
                field for field in self.fields if field not in self._grouped_fields
            ]
            self._aggregations = aggregations

        else:
            # If aggregations are not supplied, group the rest by the last field
            *self._grouped_fields, self._grouping_field = self.fields
            # Use default aggregations
            self._aggregations = {
                field: GroupBy.NUNIQUE if Field(field).categorical else GroupBy.SUM
                for field in self._grouped_fields
            }

    def groupby(self):
        """Aggregate and group the current DataFrame."""
        grouped = self._df.groupby(self._grouping_field)[self._grouped_fields]
        self._df = grouped.agg(
            **{
                field: (field, aggregation)
                for field, aggregation in self._aggregations.items()
            }
        ).reset_index()

    def apply_sort(self):
        # Use custom sort if provided
        if self.sort:
            self._df = self._df.sort_values(
                by=self.x_axis if self.sort.axis == Text.X_AXIS else self.y_axis,
                ascending=self.sort.ascending,
            )

        # By default, sort by grouped field unless you were grouping by a date
        elif not self._grouping_field.temporal:
            self._df = self._df.sort_values(by=self._grouped_fields[0], ascending=True)

    def get_label(self, field: Field, label_type="axis"):
        """
        Returns the label for a Field.
        """
        # Customisation
        if field == self.x_axis and self.x_label:
            return self.x_label
        if field == self.y_axis and self.y_label:
            return self.y_label

        label = field.axis_label if label_type == "axis" else field.title_label

        # If aggregation exists, add its prefix
        if field in self._aggregations:
            agg = self._aggregations[field]
            prefix = agg.axis_prefix if label_type == "axis" else agg.title_prefix
            return prefix + label
        return label

    def get_axis_label(self, field: Field):
        return self.get_label(field, label_type="axis")

    def get_title_label(self, field: Field):
        return self.get_label(field, label_type="title")

    def make_figure(self):
        primary_field, secondary_field, *tertiary_field = self.fields
        title = (
            self.title
            or f"{self.get_title_label(primary_field)} by {self.get_title_label(secondary_field)}"
        )
        labels = {field: self.get_axis_label(field) for field in self.fields}

        self._fig = self.plot_type(
            self._df,
            x=self.x_axis,
            y=self.y_axis,
            title=title,
            labels=labels,
            log_x=self.x_log,
            log_y=self.y_log,
            # Add annotations if 3 vars
            text=tertiary_field[0] if tertiary_field else None,
        )

    def add_moving_average_line(self, window: int, label: str = None):
        """
        Adds a new line trace for a moving average of the Y-axis.

        Parameters:
        - window: The window size (e.g., 7 for weekly, 30 for monthly).
        - label: Optional label for the trace in the legend. Defaults to "Weekly/Monthly Moving Avg", or "(window)-Day Moving Avg".
        """
        # Calculate the rolling average
        x_values = self._fig.data[0].x
        y_values = pd.Series(self._fig.data[0].y)
        ma_values = y_values.rolling(window=window, min_periods=3).mean()

        if label is None:
            periods = {7: "Weekly", 30: "Monthly"}
            label = f"{periods.get(window, f'{window}-Day')} Moving Avg"

        # Add a new trace for the moving average
        self._fig.add_trace(
            dict(
                x=x_values,
                y=ma_values,
                mode="lines",
                name=label,
                line=dict(dash="dot"),
            )
        )

        # Add legend if not added already
        self._fig.update_traces(selector=0, name="Daily", showlegend=True)
        return self

    def format_figure(self):
        """
        Apply formatting to the current figure.
        """
        layout_kwargs = {}

        # Set 1 tick per unit if bar plot and X-axis is hour or day
        if self.x_axis in {Field.HOUR, Field.DAY} and self.plot_type == Plot.SCATTER:
            layout_kwargs["xaxis"] = dict(dtick=1)

        # Update titles if log scale and default labels
        if self.x_log and not self.x_label:
            new_title = f"{self._fig.layout.xaxis.title.text} (log scale)"
            layout_kwargs.setdefault("xaxis", {})["title"] = new_title
        if self.y_log and not self.y_label:
            new_title = f"{self._fig.layout.yaxis.title.text} (log scale)"
            layout_kwargs.setdefault("yaxis", {})["title"] = new_title

        # Apply combined layout
        self._fig.update_layout(**layout_kwargs)

        # Format annotations if scatter plot
        if self.plot_type == Plot.SCATTER:
            self._fig.update_traces(textposition="top center", textfont_size=10)

        # Add rolling averages
        for window in self.moving_averages:
            self.add_moving_average_line(window)

    def build(self):
        self.add_fields()
        self.apply_filters()
        self.set_aggregations()
        self.groupby()
        self.apply_sort()
        self.make_figure()
        self.format_figure()
        return self._fig
