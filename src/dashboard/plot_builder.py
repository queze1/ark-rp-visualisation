"""
Reminder:
Figure = The Plotly object (e.g. self._fig, make_figure())
Graph = The Dash component/UI (e.g. dcc.Graph, match_graph, register_graph_callbacks)
Plot = The type or logic (e.g. PlotBuilder, PlotType.LINE, plot_type)
"""

from dataclasses import dataclass
from dataclasses import field as data_field
from typing import Any, Optional

import pandas as pd
from dash import Input, Output, State, ctx

from dashboard.callback_patterns import (
    match_agg_dropdowns,
    match_axes,
    match_fields,
    match_filter_operators,
    match_filter_types,
    match_filter_values,
    match_fullscreen_button,
    match_fullscreen_button_icon,
    match_graph,
    match_mavg_7,
    match_mavg_30,
    match_sort_axis,
    match_sort_order,
    match_title_input,
    match_update_graph,
    match_x_label,
    match_x_log,
    match_y_label,
    match_y_log,
)
from data_loader import DataLoader
from enums import Field, Filter, GroupBy, Operator, PlotType, Tab, Text
from logging_setup import get_logger

logger = get_logger(__name__)


def _add_derived_field(df: pd.DataFrame, field: Field) -> pd.DataFrame:
    """Adds a derived field to the DataFrame if it doesn't exist."""
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
                window for window, enabled in moving_averages.items() if enabled
            ],
            sort=SortConfig.from_raw(sort_order, sort_axis)
            if sort_order and sort_axis
            else None,
        )


class PlotBuilder:
    def __init__(
        self,
        plot_type: PlotType,
        axis_config: AxisConfig,
        filter_config: FilterConfig,
        figure_config: FigureConfig,
    ):
        self._df = DataLoader().df.copy()
        self._fig = None

        self.plot_type = plot_type
        self.axis_config = axis_config
        self.filter_config = filter_config
        self.figure_config = figure_config

    def groupby(self):
        """Aggregate and group the current DataFrame."""
        *rest, grouping_field = self.axis_config.fields
        grouped = self._df.groupby(grouping_field, observed=False)[rest]
        self._df = grouped.agg(self.axis_config.aggregations).reset_index()

    def apply_sort(self):
        sort = self.figure_config.sort

        if sort:
            by_axis = (
                self.axis_config.x_axis
                if sort.axis == Text.X_AXIS
                else self.axis_config.y_axis
            )
            self._df = self._df.sort_values(
                by=by_axis,
                ascending=sort.ascending,
            )
        else:
            # Fallback logic
            *_, grouping_field = self.axis_config.fields
            if not grouping_field.temporal:
                primary_field = self.axis_config.fields[0]
                self._df = self._df.sort_values(by=primary_field, ascending=True)

    def get_label(self, field: Field, label_type="axis"):
        """
        Returns the label for a Field.
        """
        # Customisation
        if field == self.axis_config.x_axis and self.figure_config.x_label:
            return self.figure_config.x_label
        if field == self.axis_config.y_axis and self.figure_config.y_label:
            return self.figure_config.y_label

        label = field.axis_label if label_type == "axis" else field.title_label

        # If aggregation exists, add its prefix
        if field in self.axis_config.aggregations:
            agg = self.axis_config.aggregations[field]
            prefix = agg.axis_prefix if label_type == "axis" else agg.title_prefix
            return prefix + label
        return label

    def make_figure(self):
        primary_field, secondary_field, *tertiary_field = self.axis_config.fields

        title = (
            self.figure_config.title
            or f"{self.get_label(primary_field, 'title')} by {self.get_label(secondary_field, 'title')}"
        )
        labels = {
            field: self.get_label(field, "axis") for field in self.axis_config.fields
        }

        self._fig = self.plot_type(
            self._df,
            x=self.axis_config.x_axis,
            y=self.axis_config.y_axis,
            title=title,
            labels=labels,
            log_x=self.figure_config.x_log,
            log_y=self.figure_config.y_log,
            text=tertiary_field[0] if tertiary_field else None,
        )

    def add_moving_average_line(self, window: int, label: Optional[str] = None):
        """
        Adds a new line trace for a moving average of the Y-axis.

        Parameters:
        - window: The window size (e.g., 7 for weekly, 30 for monthly).
        - label: Optional label for the trace in the legend. Defaults to "Weekly/Monthly Moving Avg", or "(window)-Day Moving Avg".
        """
        if self._fig is None:
            raise ValueError("Figure not created yet")

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
        if self._fig is None:
            raise ValueError("Figure does not exist")

        layout_kwargs = {}

        # Set 1 tick per unit if specific conditions met
        if (
            self.axis_config.x_axis in {Field.HOUR, Field.DAY}
            and self.plot_type == PlotType.SCATTER
        ):
            layout_kwargs["xaxis"] = dict(dtick=1)

        # Log scale titles
        if self.figure_config.x_log and not self.figure_config.x_label:
            new_title = f"{self._fig.layout.xaxis.title.text} (log scale)"
            layout_kwargs.setdefault("xaxis", {})["title"] = new_title
        if self.figure_config.y_log and not self.figure_config.y_label:
            new_title = f"{self._fig.layout.yaxis.title.text} (log scale)"
            layout_kwargs.setdefault("yaxis", {})["title"] = new_title

        self._fig.update_layout(**layout_kwargs)

        if self.plot_type == PlotType.SCATTER:
            self._fig.update_traces(textposition="top center", textfont_size=10)

        # Add moving averages from figure_config
        for window in self.figure_config.moving_averages:
            self.add_moving_average_line(window)

    def build(self):
        # 1. Prepare data (add derived columns needed by axes and filters)
        self._df = self.axis_config.prepare_dataframe(self._df)
        self._df = self.filter_config.prepare_dataframe(self._df)

        # 2. Filter data
        self._df = self.filter_config.apply(self._df)

        # 3. Process and plot
        self.groupby()
        self.apply_sort()
        self.make_figure()
        self.format_figure()

        return self._fig


def register_graph_callbacks(app):
    def render_graph(
        n_clicks,
        selected_fields,
        selected_axes,
        selected_aggregations,
        filters,
        customisation,
    ):
        if n_clicks is None or not all(selected_fields) or not ctx.triggered_id:
            return dict(
                fig={},
                fullscreen_url="#",
                fullscreen_disabled=True,
            )

        active_tab = Tab(ctx.triggered_id["tab"])

        # Log graph creation
        summary = f"""
        User created a graph:
            Tab: {active_tab.label}
            {selected_axes[0]}: {selected_fields[0]}
            {selected_axes[1]}: {selected_fields[1]}
            Aggregations: {selected_aggregations}
            Filters: {filters}
            Customizations: {customisation}
        """
        logger.info(summary.strip())

        # TODO: JSON dumps the graph inputs, then zlib compress and convert to b64, then put those options in a new /graph/ route
        return dict(
            fig=PlotBuilder(
                plot_type=PlotType(active_tab.plot_type),
                axis_config=AxisConfig.from_raw(
                    selected_fields=selected_fields,
                    selected_axes=selected_axes,
                    selected_aggregations=selected_aggregations,
                ),
                filter_config=FilterConfig.from_raw(*filters),
                figure_config=FigureConfig.from_raw(**customisation),
            ).build(),
            fullscreen_url="https://dash.plotly.com/",
            fullscreen_disabled=False,
        )

    app.callback(
        output=dict(
            fig=Output(match_graph, "figure"),
            fullscreen_url=Output(match_fullscreen_button, "href"),
            fullscreen_disabled=Output(match_fullscreen_button_icon, "disabled"),
        ),
        inputs=dict(
            n_clicks=Input(match_update_graph, "n_clicks"),
            selected_fields=State(match_fields, "value"),
            selected_axes=State(match_axes, "children"),
            selected_aggregations=State(
                match_agg_dropdowns,
                "value",
            ),
            filters=(
                State(
                    match_filter_types,
                    "value",
                ),
                State(
                    match_filter_operators,
                    "value",
                ),
                State(
                    match_filter_values,
                    "value",
                ),
            ),
            customisation=dict(
                title=State(match_title_input, "value"),
                x_label=State(match_x_label, "value"),
                y_label=State(match_y_label, "value"),
                moving_averages={
                    7: State(match_mavg_7, "checked"),
                    30: State(match_mavg_30, "checked"),
                },
                sort_order=State(match_sort_order, "value"),
                sort_axis=State(match_sort_axis, "value"),
                x_log=State(match_x_log, "checked"),
                y_log=State(match_y_log, "checked"),
            ),
        ),
    )(render_graph)
