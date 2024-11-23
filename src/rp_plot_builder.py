import pandas as pd
import plotly.express as px


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
    MESSAGES = "messages"


class RPPlotBuilder:
    def __init__(self, df: pd.DataFrame):
        self._df = df
        self._actions = []

    def messages(self):
        self._actions.append(Field.MESSAGES)
