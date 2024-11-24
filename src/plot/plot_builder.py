import pandas as pd


from .enums import Field, GroupBy, Plot
from .database_transformer import DatabaseTransformer
from .plot_transformer import PlotTransformer


class PlotBuilder:
    def __init__(self, df: pd.DataFrame):
        self._database = DatabaseTransformer(df)
        self._plot = None

    # Aliases for data selection
    def author_id(self):
        self._database.add_field(Field.AUTHOR_ID)
        return self

    def author(self):
        self._database.add_field(Field.AUTHOR)
        return self

    def date(self):
        self._database.add_field(Field.DATE)
        return self

    def hour(self):
        self._database.add_field(Field.HOUR)
        return self

    def day(self):
        self._database.add_field(Field.DAY)
        return self

    def content(self):
        self._database.add_field(Field.CONTENT)
        return self

    def attachments(self):
        self._database.add_field(Field.ATTACHMENTS)
        return self

    def reactions(self):
        self._database.add_field(Field.REACTIONS)
        return self

    def word_count(self):
        self._database.add_field(Field.WORD_COUNT)
        return self

    def channel_name(self):
        self._database.add_field(Field.CHANNEL_NAME)
        return self

    def scene_id(self):
        self._database.add_field(Field.SCENE_ID)
        return self

    # Aliases for group by
    def sum(self):
        self._database.group_by(GroupBy.SUM)
        return self

    def mean(self):
        self._database.group_by(GroupBy.MEAN)
        return self

    def count(self):
        self._database.group_by(GroupBy.COUNT)
        return self

    def nunique(self):
        self._database.group_by(GroupBy.NUNIQUE)
        return self

    def value_counts(self):
        self._database.value_counts()
        return self

    def sort(self, field: Field, ascending: bool = True):
        self._database.sort(field, ascending)
        return self

    def _create_plot(self, plot_type: Plot):
        """
        Create a plot from the current DataFrame state.
        """
        # Pass current dataframe and history to transformer
        df = self._database.dataframe
        history = self._database.history
        self._plot = PlotTransformer(df, history, plot_type)
        return self

    # Aliases for _plot
    def bar(self):
        """
        Create a bar plot from the current DataFrame state.
        """
        return self._create_plot(Plot.BAR)

    def scatter(self):
        """
        Create a scatter plot from the current DataFrame state.
        """
        return self._create_plot(Plot.SCATTER)

    def line(self):
        """
        Create a line plot from the current DataFrame state.
        """
        return self._create_plot(Plot.LINE)

    def reset(self):
        """
        Reset the current plot.
        """
        self._database.reset()
        return self

    @property
    def figure(self) -> pd.DataFrame:
        """
        Return the current figure.
        """
        if self._plot is None:
            raise ValueError("Plot has not been created yet")
        return self._plot._fig
