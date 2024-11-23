import pandas as pd


class Field:
    AUTHOR_ID = "authorId"
    AUTHOR = "author"
    DATE = "date"
    CONTENT = "content"
    ATTACHMENTS = "attachments"
    REACTIONS = "reactions"
    WORD_COUNT = "wordCount"
    CHANNEL_NAME = "channelName"
    SCENE_ID = "sceneId"


class RPPlotBuilder:
    def __init__(self, df: pd.DataFrame):
        self._df = df
        self._actions = []

    # def line(self, x, y):
