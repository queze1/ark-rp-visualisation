from .enums import Field, GroupBy, Filter


class Metadata:
    def __init__(self):
        """
        Metadata for plot operations.
        """
        self._store = {}
        self._filters = []

    def add_group_by(self, field: Field, aggregation: GroupBy):
        """
        Apply a group-by operation to a field.
        """
        # Ensure the field has a dynamic metadata store
        if field not in self._store:
            self._store[field] = {}

        # Mutate the description and label for the specific aggregation
        self._store[field]["description"] = (
            f"{aggregation.description_prefix}{field.description}"
        )
        self._store[field]["label"] = f"{aggregation.label_prefix}{field.label}"

    def add_filter(self, filter: Filter, field: Field, value):
        """
        Add a filter description to the internal state.
        """
        self._filters.append(f"{field.label} {filter.symbol} {value}")

    def add_cumulative(self, field: Field, result_field_name: str):
        """
        Add metadata for a cumulative field.
        """
        # Add a new dynamic entry in the store
        self._store[result_field_name] = {
            "description": f"Cumulative {field.description}",
            "label": f"Number of {field.label}",
        }

    def get_filters_description(self) -> str:
        """
        Return the combined description of all applied filters.
        """
        return f"({', '.join(self._filters)})" if self._filters else ""

    def get_field_metadata(self, field: Field):
        """
        Return the metadata for a field. If it's not dynamically
        modified in the `_store`, return the default metadata from `Field`.
        """
        # Check if the key exists in the internal store
        if field in self._store:
            return self._store[field]

        # Fall back to the default metadata in the Field enum
        field_enum = Field(field)
        return {"description": field_enum.description, "label": field_enum.label}

    def generate_plot_labels(self, x_field: Field, y_field: Field):
        """
        Dynamically generate labels and title for a plot using metadata.
        """
        x_metadata = self.get_field_metadata(x_field)
        y_metadata = self.get_field_metadata(y_field)
        filters_description = self.get_filters_description()

        title = f"{y_metadata['description']} by {x_metadata['description']} {filters_description}"

        return {
            "labels": {
                x_field: x_metadata["label"],
                y_field: y_metadata["label"],
            },
            "title": title,
        }
