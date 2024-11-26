from plot.data_loader import DataLoader
from plot.plot_builder import PlotBuilder, Field
from plot.enums import GroupBy


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

    def unique_authors_by_date_line(self):
        self._builder.date().author().nunique().line()
        return self

    def total_word_count_by_authors_scatter(self):
        self._builder.author().word_count().sum().sort(
            Field.WORD_COUNT, ascending=False
        ).filter_min(Field.WORD_COUNT, 50).scatter(
            Field.WORD_COUNT, Field.AUTHOR
        ).xlog()
        return self

    def messages_by_hour_bar(self):
        self._builder.hour().value_counts().scatter()
        return self

    def messages_by_date_line(self):
        self._builder.date().value_counts().sort(Field.DATE).line()
        return self

    def total_reactions_by_date(self):
        self._builder.date().reaction_count().sum().sort(Field.DATE).line()
        return self

    def total_word_count_by_unique_days_by_user_scatter(self):
        self._builder.author().word_count().date().agg(
            {Field.WORD_COUNT: GroupBy.SUM, Field.DATE: GroupBy.NUNIQUE}
        ).scatter().xlog().ylog()
        return self

    def word_counts_by_queze(self):
        self._builder.filter_equals(
            Field.AUTHOR, "queze"
        ).word_count().value_counts().scatter()
        return self

    def total_word_count_by_messages_by_user_scatter(self):
        self._builder.author().word_count().count().sum().scatter().xlog().ylog()
        return self


if __name__ == "__main__":
    builder = PlotBuilderHelper()
    # builder.unique_authors_by_date_line().show()
    # builder.total_word_count_by_authors_scatter().show()
    # builder.messages_by_hour_bar().show()
    # builder.messages_by_date_line().show()
    # builder.total_reactions_by_date().show()
    # builder.total_word_count_by_unique_days_by_user_scatter().show()
    # builder.word_counts_by_queze().show()
    # builder.total_word_count_by_messages_by_user_scatter().show()
