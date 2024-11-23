import importlib
from multiprocessing import Value
import os
import sys
from enum import Enum, StrEnum, auto
import itertools

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
    WORD_COUNT = "wordCount"
    CHANNEL_NAME = "channelName"
    SCENE_ID = "sceneId"


class Action(Enum):
    BY = auto()


class Plot(Enum):
    BAR = auto()
    SCATTER = auto()


class ArgTypes(StrEnum):
    X_AXIS = "x_axis"
    Y_AXIS = "y_axis"
    PLOT = "plot"


class RPPlotBuilder:
    def __init__(self, df: pd.DataFrame):
        self._df = df
        self._steps = []

    # Data selection
    def author_id(self):
        self._steps.append(Field.AUTHOR_ID)
        return self

    def author(self):
        self._steps.append(Field.AUTHOR)
        return self

    def date(self):
        self._steps.append(Field.DATE)
        return self

    def hour(self):
        self._steps.append(Field.HOUR)
        return self

    def day(self):
        self._steps.append(Field.DAY)
        return self

    def content(self):
        self._steps.append(Field.CONTENT)
        return self

    def attachments(self):
        self._steps.append(Field.ATTACHMENTS)
        return self

    def reactions(self):
        self._steps.append(Field.REACTIONS)
        return self

    def word_count(self):
        self._steps.append(Field.WORD_COUNT)
        return self

    def channel_name(self):
        self._steps.append(Field.CHANNEL_NAME)
        return self

    def scene_id(self):
        self._steps.append(Field.SCENE_ID)
        return self

    # Separates y-axis steps from x-axis steps
    def by(self):
        self._steps.append(Action.BY)
        return self

    # Plot selection
    def bar(self):
        self._steps.append(Plot.BAR)
        return self

    def scatter(self):
        self._steps.append(Plot.SCATTER)
        return self

    def _field(self, field):
        if field == Field.HOUR:
            return self._df[Field.DATE].dt.hour
        elif field == Field.DAY:
            return self._df[Field.DATE].dt.day
        return self._df[field]

    def _plot(self, plot, current):
        kwargs = {"x": current[ArgTypes.X_AXIS], "y": current[ArgTypes.Y_AXIS]}
        if plot == Plot.BAR:
            return px.bar(**kwargs)
        elif plot == Plot.SCATTER:
            return px.scatter(**kwargs)
        raise ValueError(f"Invalid plot type {plot}")

    def _reduce(self, step, current, current_type):
        """
        Process a single step and return the new state and type.
        """
        # TODO: Lots of coupling

        # Terminate on empty step
        if step is None:
            has_plot = (
                current[ArgTypes.X_AXIS] is not None
                and current[ArgTypes.Y_AXIS] is not None
                and current[ArgTypes.PLOT] is not None
            )
            if not has_plot:
                raise ValueError("Incomplete plot")
            return None, None

        # Check if action is to load a new field
        elif step in Field:
            if current_type not in (ArgTypes.X_AXIS, ArgTypes.Y_AXIS):
                raise ValueError(
                    f"Invalid new field, expected step of type {current_type}"
                )
            elif current[current_type] is not None:
                raise ValueError(
                    f"Invalid new field, type {current_type} already has a field"
                )
            return self._field(step), current_type

        # Check for axis separator
        elif step == Action.BY:
            if current_type != ArgTypes.Y_AXIS:
                raise ValueError(
                    f"Invalid comparison, expected step of type {current_type}"
                )
            elif current[current_type] is None:
                raise ValueError(
                    f"Invalid comparison, type {current_type} has no field"
                )
            return None, ArgTypes.X_AXIS

        # Check for plot type
        elif step in Plot:
            has_axes = (current[ArgTypes.X_AXIS] is not None) and (
                current[ArgTypes.X_AXIS] is not None
            )
            if not has_axes:
                raise ValueError("Invalid plot, missing axes")
            return self._plot(step, current), ArgTypes.PLOT

        raise ValueError(f"Invalid step {step}")

    def build(self):
        """
        Build a plot by iterating over steps.
        """
        current = {ArgTypes.Y_AXIS: None, ArgTypes.X_AXIS: None, ArgTypes.PLOT: None}
        current_type = ArgTypes.Y_AXIS
        iterator = iter(self._steps)

        while True:
            step = next(iterator, None)
            new_value, current_type = self._reduce(step, current, current_type)
            if not current_type:
                break
            current[current_type] = new_value

        return current[ArgTypes.PLOT]

    @property
    def steps(self):
        return self._steps

    def reset(self):
        self._steps = []


def _main():
    # Dynamically import because of REPL things
    sys.path.append(os.getcwd())
    rp_processor = importlib.import_module("src.rp_processor")
    plots = importlib.import_module("src.plots")
    df = rp_processor.RPProcessor().process_df().df
    builder = RPPlotBuilder(df).word_count().by().author().scatter()
    plots.display_html(builder.build())


if __name__ == "__main__":
    _main()
