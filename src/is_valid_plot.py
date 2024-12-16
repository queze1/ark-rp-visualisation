"""Test file for finding valid plots."""

# Set log-scale/log-log scale by default if fits a power law (using powerlaw library) and the dataset is big

fields = {
    "date": "temporal",
    # Numeric representation, but are ordinal because hours of day/days of month have an ordering and are also categorical (1am is substantively different from 8pm)
    "hour": "ordinal",
    "day": "ordinal",
    # Can be summed or nuniqued
    "reaction_count": "numerical",  # Grey zone because is small (0-20) and sort of categorical, so can fit in bar graphs
    "word_count": "numerical",
    # Can only be aggregated using nunique
    "author": "categorical",
    # Special, corresponds to the number of items in the category
    "count": "numerical",
}


def is_valid_line(x, y):
    y_type = fields[y]

    # X and Y must be different
    if x == y:
        return False

    # X-axis should be numerical, ordered and continuous (without gaps), currently only date seems to fit
    if x != "date":
        return False

    # "(Number of) unique hours (at which messages where posted) per Day" makes sense in theory, but in practice is meaningless
    # "Unique Days of Month per Day" is just meaningless
    if y_type == "ordinal":
        return False

    # Count can be plotted without any further changes
    if y == "count":
        return "line", "count"

    # Aggregate numericals by sum
    if y_type == "numerical":
        return "line", "sum"

    # Aggregate categories by nunique
    if y_type == "categorical":
        return "line", "nunique"
    return False


def is_valid_bar(x, y):
    x_type = fields[x]
    y_type = fields[y]

    # X and Y must be different
    if x == y:
        return False

    # Bar plots are for ordered categories
    if not (x == "reaction_count" or x_type == "ordinal"):
        return False

    # Hour by Day/Day by Hour makes no sense, as does Unique Days/Hours by Reaction Count
    if y_type == "ordinal":
        return False

    # Count can be plotted without any further changes
    if y == "count":
        return "bar", "count"

    # Aggregate numericals by sum
    if y_type == "numerical":
        return "bar", "sum"

    # Aggregate categories by nunique
    if y_type == "categorical":
        return "bar", "nunique"
    return False


# Scatter groups dataset by a field, each group becomes a point on the plot, X-coord and Y-coord are two summary values on that group
def is_valid_scatter(x, y, context):
    # Exclude hour and day because then there would always be the same number of points on the plot, exclude count because that's meaningless
    if context not in ("author", "date", "word_count", "reaction_count"):
        return False


def print_valid_combinations():
    # Get a list of all fields
    field_names = list(fields.keys())

    print("Valid Line Plots:")
    for x in field_names:
        for y in field_names:
            result = is_valid_line(x, y)
            if result:
                plot_type, aggregation = result
                print(
                    f"  X: {x}, Y: {y}, Plot: {plot_type}, Aggregation: {aggregation}"
                )

    print("\nValid Bar Plots:")
    for x in field_names:
        for y in field_names:
            result = is_valid_bar(x, y)
            if result:
                plot_type, aggregation = result
                print(
                    f"  X: {x}, Y: {y}, Plot: {plot_type}, Aggregation: {aggregation}"
                )


if __name__ == "__main__":
    print_valid_combinations()
