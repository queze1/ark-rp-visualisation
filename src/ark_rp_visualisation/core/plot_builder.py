"""
Reminder:
Figure = The Plotly object (e.g. self._fig, make_figure())
Graph = The Dash component/UI (e.g. dcc.Graph, match_graph, register_graph_callbacks)
Plot = The type or logic (e.g. PlotBuilder, PlotType.LINE, plot_type)
"""

from typing import Optional

import pandas as pd

from utils.logging_setup import get_logger

from . import DataLoader
from .enums import Field, PlotType, Text
from .models import AxisConfig, FigureConfig, FilterConfig

logger = get_logger(__name__)


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

    def make_figure(self):
        primary_field, secondary_field, *tertiary_field = self.axis_config.fields
        title = self.figure_config.title or (
            f"{self.axis_config.get_label(primary_field, self.figure_config, 'title')}"
            " by "
            f"{self.axis_config.get_label(secondary_field, self.figure_config, 'title')}"
        )
        labels = {
            field: self.axis_config.get_label(field, self.figure_config, "axis")
            for field in self.axis_config.fields
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
        Add a new line trace for a moving average of the Y-axis.

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
