from rp_processor import RPProcessor
from rp_plot_builder import RPPlotBuilder, Field


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


# display_html(messages_by_hour_bar())


if __name__ == "__main__":
    df = RPProcessor().process_df().df
    builder = RPPlotBuilder(df)
    # "X date by Y nunique author"
    builder.date().author().nunique().line().build().show()
    builder.reset()
    # "X author by Y sum word count in ascending order of word count"
    builder.author().word_count().sum().ascending(
        Field.WORD_COUNT
    ).scatter().build().show()
