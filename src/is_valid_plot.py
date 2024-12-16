"""Test file for finding valid plots."""

from backend.enums import Field

# Set log-scale/log-log scale by default if fits a power law (using powerlaw library) and the dataset is big


def field_aggregation(field):
    # Count can be plotted without any further changes
    if field is Field.COUNT:
        return "count"
    # Aggregate numericals by sum
    elif field.numerical:
        return "sum"
    # Aggregate categories by nunique
    elif field.categorical:
        return "nunique"
    return None


def is_valid_line(x: Field, y: Field):
    # X and Y must be different
    if x == y:
        return False

    # Line plots are for time series
    if x is not Field.DATE:
        return False

    # Can only have one temporal variable
    if y.temporal:
        return False

    return field_aggregation(y)


def is_valid_bar(x: Field, y: Field):
    # X and Y must be different
    if x == y:
        return False

    # Bar plots are for categories
    if not x.categorical:
        return False

    # Not for time series
    if x is Field.DATE:
        return False

    # Too many scene ids for bar
    if x is Field.SCENE_END:
        return False

    # Can only have one temporal variable
    if x.temporal and y.temporal:
        return False

    return field_aggregation(y)


# Scatter groups dataset by a field, each group becomes a point on the plot, X-coord and Y-coord are two summary values on that group
def is_valid_scatter(x: Field, y: Field, context: Field):
    # Exclude count as it's meaningless
    if context is Field.COUNT:
        return False

    # Can only have one temporal summary value
    if x.temporal and y.temporal:
        return False

    return field_aggregation(x), field_aggregation(y)


def print_valid_combinations():
    print("Valid Line Plots:")
    for x in Field:
        for y in Field:
            aggregation = is_valid_line(x, y)
            if aggregation:
                print(f"  X: {x}, Y: {y}, Aggregation: {aggregation}")

    print("\nValid Bar Plots:")
    for x in Field:
        for y in Field:
            aggregation = is_valid_bar(x, y)
            if aggregation:
                print(f"  X: {x}, Y: {y}, Aggregation: {aggregation}")

    # print("\nValid Scatter Plots:")
    # for context in Field:
    #     for x in Field:
    #         for y in Field:
    #             aggregation = is_valid_scatter(x, y, context)
    #             if aggregation:
    #                 agg_x, agg_y = aggregation
    #                 print(
    #                     f"  X: {x}, Y: {y}, Aggregation X: {agg_x}, Aggregation Y: {agg_y}"
    #                 )


if __name__ == "__main__":
    print_valid_combinations()
