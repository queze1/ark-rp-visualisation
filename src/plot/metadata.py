from .enums import Field, GroupBy


class Metadata:
    def __init__(self):
        """
        Metadata for plot operations.
        """
        self._filters = []

        self._field_metadata = {
            Field.AUTHOR: {
                "description": "Users",
            },
            Field.AUTHOR_ID: {
                "description": "Users",
            },
            Field.DATE: {
                "description": "Day",
                "label": "Date",
            },
            Field.HOUR: {"description": "Hour of Day"},
            Field.DAY: {"description": "Day of Month"},
            Field.CONTENT: {"description": "Messages", "label": "Number of Messages"},
            Field.ATTACHMENTS: {
                "description": "Attachments",
            },
            Field.REACTIONS: {"description": "Reactions"},
            Field.REACTION_COUNT: {
                "description": "Number of Reactions",
                "label": "Reactions",
            },
            Field.WORD_COUNT: {
                "description": "Word Count",
                "label": "Words",
            },
            Field.CHANNEL_NAME: {"description": "Channels"},
            Field.SCENE_ID: {"description": "Scenes"},
            Field.COUNT: {"description": "Messages", "label": "Number of Messages"},
        }

        self._aggregation_metadata = {
            GroupBy.SUM: {"label_prefix": "Number of "},
            GroupBy.MEAN: {
                "description_prefix": "Average ",
                "label_prefix": "Avg. ",
            },
            GroupBy.NUNIQUE: {
                "description_prefix": "Unique ",
                "label_prefix": "Unique ",
            },
        }

    def get_field_description(self, field: Field) -> str:
        return self._field_metadata.get(field, {}).get("description", str(field))

    def get_field_label(self, field: Field) -> str:
        # Label defaults to description
        return self._field_metadata.get(field, {}).get(
            "label", self.get_field_description(field)
        )

    def get_aggregation_description(self, aggregation: GroupBy) -> str:
        return self._aggregation_metadata.get(aggregation, {}).get(
            "description_prefix", ""
        )

    def get_aggregation_label(self, aggregation: GroupBy) -> str:
        return self._aggregation_metadata.get(aggregation, {}).get("label_prefix", "")

    def set_group_by(self, field: Field, aggregation: GroupBy):
        agg_description_prefix = self.get_aggregation_description(aggregation)
        agg_label_prefix = self.get_aggregation_label(aggregation)
        self._field_metadata[field] = {
            "description": f"{agg_description_prefix}{self.get_field_description(field)}",
            "label": f"{agg_label_prefix}{self.get_field_label(field)}",
        }

    def add_filter(self, field: Field, description: str):
        """
        Add a filter description to the metadata.
        """
        self._filters.append(f"{field}: {description}")

    def get_filters_description(self) -> str:
        """
        Return the combined description of all applied filters.
        """
        return f"({', '.join(self._filters)})" if self._filters else ""

    def generate_plot_labels(
        self,
        x_field: Field,
        y_field: Field,
    ):
        """
        Dynamically generate axis labels and title.
        """
        x_label = self.get_field_label(x_field)
        y_label = self.get_field_label(y_field)
        x_description = self.get_field_description(x_field)
        y_description = self.get_field_description(y_field)

        filters_description = self.get_filters_description()
        title = f"{y_description} by {x_description} {filters_description}"

        return {
            "labels": {
                x_field: x_label,
                y_field: y_label,
            },
            "title": title,
        }
