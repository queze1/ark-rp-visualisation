import pandas as pd

from .enums import Field, GroupBy, Plot
from .database_transformer import DatabaseTransformer


class PlotBuilder:
    def __init__(self, df: pd.DataFrame):
        # Transformer for database operations
        self._database = DatabaseTransformer(df)

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

    def _plot(self, plot_type: Plot):
        """
        Create a plot from the current DataFrame state.
        """
        df = self._database.get_dataframe()
        history = self._database.get_history()

        if len(df.columns) < 2:
            raise ValueError("Not enough data columns to plot.")

        x_field, y_field = df.columns[:2]
        kwargs = {"x": x_field, "y": y_field}
        # Generate figure
        fig = plot_type(df, **kwargs)

        # Add history-based labels
        if history:
            fig.update_layout(
                title=" vs. ".join(
                    op["field"] for op in history if op["operation"] == "add_field"
                ),
            )

        return fig

    def bar(self):
        return self._plot(Plot.BAR)

    def scatter(self):
        return self._plot(Plot.SCATTER)

    def line(self):
        return self._plot(Plot.LINE)

    def reset(self):
        self._database.reset()
        return self
