import pandas as pd
from plotly.graph_objects import Figure

from .enums import Field, GroupBy, Plot
from .database_transformer import DatabaseTransformer
from .plot_transformer import PlotTransformer


class PlotBuilder:
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
    def author_id(self):
        return self._queue_add_field(Field.AUTHOR_ID)

    def author(self):
        return self._queue_add_field(Field.AUTHOR)

    def date(self):
        return self._queue_add_field(Field.DATE)

    def hour(self):
        return self._queue_add_field(Field.HOUR)

    def day(self):
        return self._queue_add_field(Field.DAY)

    def content(self):
        return self._queue_add_field(Field.CONTENT)

    def attachments(self):
        return self._queue_add_field(Field.ATTACHMENTS)

    def reactions(self):
        return self._queue_add_field(Field.REACTIONS)

    def word_count(self):
        return self._queue_add_field(Field.WORD_COUNT)

    def channel_name(self):
        return self._queue_add_field(Field.CHANNEL_NAME)

    def scene_id(self):
        return self._queue_add_field(Field.SCENE_ID)

    # Aliases for group by
    def sum(self, field=None):
        return self._queue_group_by(GroupBy.SUM, field=field)

    def mean(self, field=None):
        return self._queue_group_by(GroupBy.MEAN, field=field)

    def nunique(self, field=None):
        return self._queue_group_by(GroupBy.NUNIQUE, field=field)

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
