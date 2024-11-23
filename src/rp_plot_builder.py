import pandas as pd


class RPPlotBuilder:
    def __init__(self, df: pd.DataFrame):
        self._df = df

    @property
    def hours(self):
        hours = self._df["date"].dt.hour.reset_index()
        hours.columns = ["index", "hour"]
        return hours

    @property
    def days(self):
        days = self._df["date"].dt.day.reset_index()
        days.columns = ["index", "day"]
        return days

    @property
    def scene_id(self):
        return self._df["sceneId"].reset_index()

    @property
    def author(self):
        return self._df["author"].reset_index()

    @property
    def author_id(self):
        return self._df["authorId"].reset_index()

    @property
    def channel_name(self):
        return self._df["channelName"].reset_index()

    @property
    def date(self):
        return self._df["date"].reset_index()

    @property
    def word_count(self):
        word_count = self._df["content"].str.split().str.len().reset_index()
        word_count.columns = ["index", "wordCount"]
        return word_count
