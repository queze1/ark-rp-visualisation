from enum import StrEnum
from itertools import chain

import pandas as pd
import plotly.express as px


class Field(StrEnum):
    AUTHOR_ID = "authorId"
    AUTHOR = "author"
    DATE = "date"
    HOUR = "hour"
    DAY = "day"
    CONTENT = "content"
    ATTACHMENTS = "attachments"
    REACTIONS = "reactions"
    REACTION_COUNT = "reactionCount"
    WORD_COUNT = "wordCount"
    CHANNEL_NAME = "channelName"
    SCENE_ID = "sceneId"


class GroupBy(StrEnum):
    SUM = "sum"
    MEAN = "mean"
    COUNT = "count"
    NUNIQUE = "nunique"

    def __call__(self, obj):
        if self is GroupBy.SUM:
            return obj.sum()
        elif self is GroupBy.MEAN:
            return obj.mean()
        elif self is GroupBy.COUNT:
            return obj.count()
        elif self is GroupBy.NUNIQUE:
            return obj.nunique()
        raise NotImplementedError(f"{self.value} groupby is not implemented.")


class Plot(StrEnum):
    BAR = "bar"
    SCATTER = "scatter"
    LINE = "line"

    def __call__(self, *args, **kwargs):
        if self is Plot.BAR:
            return px.bar(*args, **kwargs)
        elif self is Plot.SCATTER:
            return px.scatter(*args, **kwargs)
        elif self is Plot.LINE:
            return px.line(*args, **kwargs)
        raise NotImplementedError(f"{self.value} plot is not implemented.")


class RPPlotBuilder:
    def __init__(self, df: pd.DataFrame):
        self._df = df
        self._steps = []

    def _add_step(self, step):
        """
        Generic method to add a step.
        """
        self._steps.append(step)
        return self

    @staticmethod
    def _generate_step_methods():
        """
        Dynamically generate `.author, `.sum()`, `.bar()`, etc.,
        based on `Field`, `GroupBy` and `Plot` enums and bind them to the class.
        """
        for step in chain(Field, GroupBy, Plot):
            # Convert enum names to lowercase for method names
            name = step.name.lower()

            def method(self, step=step):
                return self._add_step(step)

            # Dynamically create and attach a method for each step
            setattr(RPPlotBuilder, name, method)

    def _field(self, field: Field):
        """
        Get a column of the specified field.
        """
        if field == Field.HOUR:
            return self._df[Field.DATE].dt.hour
        elif field == Field.DAY:
            return self._df[Field.DATE].dt.day
        elif field == Field.DATE:
            return self._df[Field.DATE].dt.date
        return self._df[field]

    def _plot(self, plot: Plot, df: pd.DataFrame):
        x_field, y_field = df
        kwargs = {"x": x_field, "y": y_field}
        return plot(df, **kwargs)

    def build(self):
        """
        Build a plot by iterating over steps.
        """
        current = pd.DataFrame()
        for step in self._steps:
            if step in Field:
                # Join the new field to the current DataFrame
                current = pd.concat([current, self._field(step)], axis=1)
            elif step in GroupBy:
                field1, field2 = current
                # Put second field (e.g. number of messages) in groups determined by first field (e.g. author)
                groupby = current.groupby(field1)[field2]
                # Aggregate the groups and convert back to Dataframe
                current = step(groupby).reset_index()
            elif step in Plot:
                # Create a plot from the current DataFrame
                current = self._plot(step, current)

        return current

    @property
    def steps(self):
        return self._steps

    def reset(self):
        self._steps = []


RPPlotBuilder._generate_step_methods()
