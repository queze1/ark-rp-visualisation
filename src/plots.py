from plot.data_loader import DataLoader
from plot.plot_builder import PlotBuilder, Field


class PlotBuilderHelper:
    """
    Plot building pipelines for testing.
    """

    def __init__(self):
        df = DataLoader().load_data().df
        self._builder = PlotBuilder(df)

    def show(self):
        """Build the current plot, show it, then reset."""
        self._builder.build().figure.show()
        self._builder.reset()
        return self

    def date_by_unique_author_line(self):
        self._builder.date().author().nunique().line()
        return self

    def author_by_total_word_count_scatter(self):
        self._builder.author().word_count().sum().sort(
            Field.WORD_COUNT, ascending=False
        ).scatter(Field.WORD_COUNT, Field.AUTHOR).xlog()
        return self

    def messages_by_hour_bar(self):
        self._builder.hour().value_counts().bar()
        return self

    def messages_by_date_line(self):
        self._builder.date().value_counts().sort(Field.DATE).line()
        return self


if __name__ == "__main__":
    builder = PlotBuilderHelper()
    # builder.date_by_unique_author_line().show()
    builder.author_by_total_word_count_scatter().show()
    # builder.messages_by_hour_bar().show()
    # builder.messages_by_date_line().show()
