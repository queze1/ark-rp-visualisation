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


class Mutator(StrEnum):
    VALUE_COUNTS = "value_counts"
    ASCENDING = "ascending"
    DESCENDING = "descending"

    def __call__(self, df: pd.DataFrame, *args):
        if self is Mutator.VALUE_COUNTS:
            # Assumes that the DataFrame has only one field (as this overwrites all others)
            # Sorts by value, instead of count
            (field,) = df
            return df[field].value_counts().sort_index().reset_index()
        elif self is Mutator.ASCENDING:
            (field,) = args
            return df.sort_values(by=field, ascending=True)
        elif self is Mutator.DESCENDING:
            (field,) = args
            return df.sort_values(by=field, ascending=False)
        raise NotImplementedError(f"{self.value} mutator is not implemented.")


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

    def _add_step(self, step, *args):
        """
        Generic method to add a step with optional args.
        """
        self._steps.append((step, *args))
        return self

    @staticmethod
    def _generate_step_methods():
        """
        Dynamically generate methods to add step enums for Field, GroupBy, Plot, Mutator, etc.
        """
        for step in chain(Field, GroupBy, Plot, Mutator):
            name = step.name.lower()

            def method(self, step=step, *args):
                return self._add_step(step, *args)

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
        """
        First column for X-axis, second for Y-axis.
        """
        x_field, y_field = df
        kwargs = {"x": x_field, "y": y_field}
        return plot(df, **kwargs)

    def build(self):
        """
        Build a plot by iterating over steps.
        """
        current = pd.DataFrame()
        for step, *args in self._steps:
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
            elif step in Mutator:
                # Handle mutators on the DataFrame
                current = step(current, *args)

        return current

    @property
    def steps(self):
        return self._steps

    def reset(self):
        self._steps = []


RPPlotBuilder._generate_step_methods()
