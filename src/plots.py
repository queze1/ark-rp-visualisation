from plot.data_loader import DataLoader
from plot.plot_builder import PlotBuilder, Field


# def messages_by_hour_bar():
#     messages_by_hour = df["date"].dt.hour.value_counts().sort_index()
#     messages_by_hour = messages_by_hour.reset_index()
#     messages_by_hour.columns = ["hour", "count"]
#     fig = px.bar(
#         messages_by_hour,
#         x="hour",
#         y="count",
#         labels={"hour": "Hour of the Day", "count": "Number of Messages"},
#         title="Messages by Hour",
#     )

#     fig.update_layout(
#         xaxis=dict(
#             tickmode="linear",  # Ensure ticks are evenly spaced (not auto-selected)
#             tick0=0,  # Start ticks at 0
#             dtick=1,  # Show ticks every 1 unit
#         )
#     )
#     return fig


def date_by_unique_author_line(builder):
    # "X date by Y nunique author"
    return builder.date().author().nunique().line()


def author_by_total_word_count_scatter(builder):
    # "X author by Y sum word count in ascending order of word count"
    return (
        builder.author()
        .word_count()
        .sum()
        .ascending(
            Field.WORD_COUNT,
        )
        .scatter()
    )


if __name__ == "__main__":
    df = DataLoader().load_data().df
    builder = PlotBuilder(df)

    date_by_unique_author_line(builder).build().show()
    builder.reset()
