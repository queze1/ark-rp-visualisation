# import pandas as pd


# class RPPlotBuilder:
#     def __init__(self, df: pd.DataFrame):
#         self._df = df

#     @property
#     def hours(self):
#         return self._df["date"].dt.hour

#     @property
#     def days(self):
#         return self._df["date"].dt.day

#     @property
#     def scene_id(self):
#         return self._df["sceneId"]

#     @property
#     def author(self):
#         return self._df["author"]

#     @property
#     def author_id(self):
#         return self._df["authorId"]

#     @property
#     def channel_name(self):
#         return self._df["channelName"]

#     @property
#     def date(self):
#         return self._df["date"]

#     @property
#     def word_count(self):
#         return self._df["wordCount"]
