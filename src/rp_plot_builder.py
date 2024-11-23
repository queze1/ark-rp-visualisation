import importlib
import os
import sys
from enum import Enum, StrEnum, auto

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
    GROUP_BY = auto()
    SUM = auto()
    VALUE_COUNTS = auto()


class Plot(Enum):
    BAR = auto()
    SCATTER = auto()


class StepType(StrEnum):
    X_AXIS = "x_axis"
    Y_AXIS = "y_axis"
    PLOT = "plot"


class RPPlotBuilder:
    def __init__(self, df: pd.DataFrame):
        self._df = df
        self._x_steps = []
        self._y_steps = []
        self._groupby_steps = []
        self._plot_steps = []
        self._current_step_type = StepType.Y_AXIS

    def _add_field(self, field):
        """
        Generic method to add a field to the steps.
        """

        if self._current_step_type == StepType.X_AXIS:
            step_list = self._x_steps
        elif self._current_step_type == StepType.Y_AXIS:
            step_list = self._y_steps
        else:
            raise ValueError(
                f"Invalid new field, expected step of type {self._current_step_type}"
            )

        # Check if a field has alreay been set for this axis
        if step_list:
            raise ValueError(
                f"Invalid new field, type {self._current_step_type} already has a field"
            )

        step_list.append(field)
        return self

    @staticmethod
    def _generate_field_methods():
        """
        Dynamically generate `.author, `.word_count()`, etc.,
        based on the `Field` enum and bind them to the class.
        """
        for field in Field:
            # Convert Field enum names to lowercase for method names
            name = field.name.lower()

            def method(self, field=field):
                self._add_step(field)
                return self

            # Dynamically create and attach a method for each field
            setattr(RPPlotBuilder, name, method)

    def by(self):
        """
        Transition from building Y-axis to building X-axis.
        """
        if self._current_step_type != StepType.Y_AXIS:
            raise ValueError(
                f"Invalid grouping, expected step of type {self._current_step_type}"
            )
        elif not self._y_steps:
            raise ValueError(
                f"Invalid grouping, type {self._current_step_type} is empty"
            )
        self._current_step_type = StepType.X_AXIS
        return self

    def group_by(self):
        """
        Change axis, and mark Y-axis to be grouped by X-axis.
        """
        self.by()
        self._groupby_steps.append(Action.GROUP_BY)
        return self

    def value_counts(self):
        """
        Skip setting X-axis, set new Y-axis to be value counts of X-axis.
        """
        if self._current_step_type != StepType.Y_AXIS:
            raise ValueError(
                f"Invalid value counts, expected step of type {self._current_step_type}"
            )
        elif self._y_steps is None:
            raise ValueError(
                f"Invalid value counts, type {self._current_step_type} is empty"
            )
        self._current_step_type = StepType.PLOT
        self._x_steps = self._y_steps
        self._y_steps = [Action.VALUE_COUNTS]
        return self

    def sum(self):
        if not self._groupby_steps:
            raise ValueError("Invalid sum, no group by declared")
        elif self._current_step_type not in (StepType.X_AXIS, StepType.Y_AXIS):
            raise ValueError(
                f"Invalid sum, expected step of type {self._current_step_type}"
            )
        self._groupby_steps.append(Action.SUM)

    # Plot selection
    def _set_plot(self, plot_type):
        has_axes = self._x_steps and self._y_steps
        if not has_axes:
            raise ValueError("Invalid plot, missing axes")

    def bar(self):
        self._plot_steps.append(Plot.BAR)
        return self

    def scatter(self):
        self._plot_steps.append(Plot.SCATTER)
        return self

    def _field(self, field):
        if field == Field.HOUR:
            return self._df[Field.DATE].dt.hour
        elif field == Field.DAY:
            return self._df[Field.DATE].dt.day
        return self._df[field]

    # def _plot(self, plot, current):
    #     kwargs = {"x": current[StepType.X_AXIS], "y": current[StepType.Y_AXIS]}
    #     if plot == Plot.BAR:
    #         return px.bar(**kwargs)
    #     elif plot == Plot.SCATTER:
    #         return px.scatter(**kwargs)
    #     raise ValueError(f"Invalid plot type {plot}")

    # def _reduce(self, step, current, current_type):
    #     """
    #     Process a single step and return the new state and type.
    #     """
    #     # TODO: Lots of coupling

    #     # Terminate on empty step
    #     if step is None:
    #         has_plot = (
    #             current[StepType.X_AXIS] is not None
    #             and current[StepType.Y_AXIS] is not None
    #             and current[StepType.PLOT] is not None
    #         )
    #         if not has_plot:
    #             raise ValueError("Incomplete plot")
    #         return None, None

    #     # Check if action is to load a new field
    #     elif step in Field:
    #         if current_type not in (StepType.X_AXIS, StepType.Y_AXIS):
    #             raise ValueError(
    #                 f"Invalid new field, expected step of type {current_type}"
    #             )
    #         elif current[current_type] is not None:
    #             raise ValueError(
    #                 f"Invalid new field, type {current_type} already has a field"
    #             )
    #         return self._field(step), current_type

    #     # Check for axis separator
    #     elif step == Action.BY:
    #         if current_type != StepType.Y_AXIS:
    #             raise ValueError(
    #                 f"Invalid comparison, expected step of type {current_type}"
    #             )
    #         elif current[current_type] is None:
    #             raise ValueError(
    #                 f"Invalid comparison, type {current_type} has no field"
    #             )
    #         return None, StepType.X_AXIS

    #     # Check for plot type
    #     elif step in Plot:
    # has_axes = (current[StepType.X_AXIS] is not None) and (
    #     current[StepType.X_AXIS] is not None
    # )
    # if not has_axes:
    #     raise ValueError("Invalid plot, missing axes")
    # return self._plot(step, current), StepType.PLOT

    #     raise ValueError(f"Invalid step {step}")

    # def build(self):
    #     """
    #     Build a plot by iterating over steps.
    #     """
    #     current = {StepType.Y_AXIS: None, StepType.X_AXIS: None, StepType.PLOT: None}
    #     current_type = StepType.Y_AXIS
    #     iterator = iter(self._steps)

    #     while True:
    #         step = next(iterator, None)
    #         new_value, current_type = self._reduce(step, current, current_type)
    #         if not current_type:
    #             break
    #         current[current_type] = new_value

    #     return current[StepType.PLOT]

    def reset(self):
        self._x_steps = []
        self._y_steps = []
        self._groupby_steps = []
        self._plot_steps = []
        self._current_step_type = StepType.Y_AXIS


RPPlotBuilder._generate_field_methods()


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
