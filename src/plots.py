# import subprocess
from rp_processor import RPProcessor
# import plotly.express as px


processor = RPProcessor()
processor.process_df()
df = processor.df


# def display_html(fig):
#     VIEW_COMMAND = "wslview"
#     OUTPUT_PATH = "output/output.html"

#     fig.write_html(OUTPUT_PATH)
#     subprocess.run([VIEW_COMMAND, OUTPUT_PATH])


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
