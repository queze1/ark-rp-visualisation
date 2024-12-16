import pandas as pd
from plotly.graph_objects import Figure

from .enums import Field, Filter, GroupBy, Plot
from .database_transformer import DatabaseTransformer
from .plot_transformer import PlotTransformer


class PlotBuilder:
    """
    Pipeline for creating a plot through a series of operations.

    Wrapper over `DatabaseTransformer` and `PlotTransformer`. Operations are evaluated lazily on `.build()`.
    """

    def __init__(self, df: pd.DataFrame):
        self._database = DatabaseTransformer(df)
        self._plot = PlotTransformer()
        self._operations = []

    def _build_plot(self, plot_type: Plot, x_field=None, y_field=None):
        """
        Build a plot from the current state.
        """
        if self._plot.figure is not None:
            raise ValueError("Plot already created!")

        df = self._database.dataframe
        metadata = self._database.metadata
        self._plot.initialize(df, metadata, plot_type, x_field=x_field, y_field=y_field)
        return self

    def _queue_operation(self, func, *args, **kwargs):
        """
        Queue a lazy operation.
        """
        self._operations.append((func, args, kwargs))
        return self

    def build(self):
        """
        Execute all queued operations.
        """
        for func, args, kwargs in self._operations:
            func(*args, **kwargs)
        return self

    def _queue_add_field(self, field: Field):
        """
        Queue an add field operation.
        """
        return self._queue_operation(self._database.add_field, field)

    def _queue_group_by(self, *args, **kwargs):
        """
        Queue a group by operation.
        """
        return self._queue_operation(self._database.group_by, *args, **kwargs)

    def _queue_filter(self, *args, **kwargs):
        """
        Queue a filter operation.
        """
        return self._queue_operation(self._database.filter, *args, **kwargs)

    def sort(self, field: Field, ascending: bool = True):
        """
        Queue a sort operation.
        """
        return self._queue_operation(self._database.sort, field, ascending=ascending)

    def value_counts(self):
        """
        Queue a value counts operation.
        """
        return self._queue_operation(self._database.value_counts)

    def _queue_build_plot(self, *args, **kwargs):
        """
        Queue a build plot operation.
        """
        return self._queue_operation(self._build_plot, *args, **kwargs)

    # Aliases for data selection
    def author(self):
        return self._queue_add_field(Field.AUTHOR)

    def date(self):
        return self._queue_add_field(Field.DATE)

    def hour(self):
        return self._queue_add_field(Field.HOUR)

    def day(self):
        return self._queue_add_field(Field.DAY)

    def reactions(self):
        return self._queue_add_field(Field.REACTIONS)

    def reaction_count(self):
        return self._queue_add_field(Field.REACTION_COUNT)

    def word_count(self):
        return self._queue_add_field(Field.WORD_COUNT)

    def channel_name(self):
        return self._queue_add_field(Field.CHANNEL_NAME)

    def scene_id(self):
        return self._queue_add_field(Field.SCENE_ID)

    def count(self):
        return self._queue_add_field(Field.COUNT)

    # Aliases for group by
    def sum(self, field=None):
        return self._queue_group_by(GroupBy.SUM, field=field)

    def mean(self, field=None):
        return self._queue_group_by(GroupBy.MEAN, field=field)

    def nunique(self, field=None):
        return self._queue_group_by(GroupBy.NUNIQUE, field=field)

    def agg(self, aggregations: dict[Field, GroupBy]):
        return self._queue_operation(self._database.group_by_multiple, aggregations)

    # Aliases for filters
    def filter_min(self, field: Field, value):
        return self._queue_filter(Filter.MIN, field, value)

    def filter_max(self, field: Field, value):
        return self._queue_filter(Filter.MAX, field, value)

    def filter_equals(self, field: Field, value):
        return self._queue_filter(Filter.EQUAL, field, value)

    # Aliases for creating derived fields
    def cumulative(self, field: Field, result_field=None):
        return self._queue_operation(
            self._database.cumulative,
            field,
            result_field=result_field,
        )

    # Aliases for plot creation
    def bar(self, x_field=None, y_field=None):
        """
        Create a bar plot.
        """
        return self._queue_build_plot(Plot.BAR, x_field=x_field, y_field=y_field)

    def scatter(self, x_field=None, y_field=None):
        """
        Create a scatter plot.
        """
        return self._queue_build_plot(Plot.SCATTER, x_field=x_field, y_field=y_field)

    def line(self, x_field=None, y_field=None):
        """
        Create a line plot.
        """
        return self._queue_build_plot(Plot.LINE, x_field=x_field, y_field=y_field)

    # Aliases for plot mutations
    def xlog(self):
        return self._queue_operation(self._plot.xlog)

    def ylog(self):
        return self._queue_operation(self._plot.ylog)

    def moving_average(self, window: int, label: str = None):
        """
        Queue an operation to add a moving average line to the figure.

        Parameters:
        - window: The size of the rolling window (e.g., 7 for weekly, 30 for monthly).
        - label: Optional label for the line trace.
        """
        return self._queue_operation(self._plot.add_moving_average_line, window, label)

    def reset(self):
        """
        Reset the current plot.
        """
        self._database.reset()
        self._plot = PlotTransformer()
        self._operations = []
        return self

    @property
    def figure(self) -> Figure:
        """
        Return the current figure.
        """
        if self._plot.figure is None:
            raise ValueError("Plot has not been created yet!")
        return self._plot.figure
