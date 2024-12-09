import pandas as pd
import pytest

from src.backend.database_transformer import DatabaseTransformer
from src.backend.enums import Field, Filter, GroupBy


@pytest.fixture
def sample_dataframe():
    data = {
        "author": ["John", "Alice", "John", "Bob", "Alice"],
        "date": pd.to_datetime(
            ["2023-11-01", "2023-11-01", "2023-11-02", "2023-11-03", "2023-11-03"]
        ),
        "word_count": [5, 10, 15, 20, 25],
        "reactions": [{"👍": 2}, {"❤️": 1}, {"👍": 1}, {}, {"👍": 3}],
    }
    return pd.DataFrame(data)


def test_initialization_preserves_original_dataframe(sample_dataframe):
    dt = DatabaseTransformer(sample_dataframe)
    pd.testing.assert_frame_equal(dt._original, sample_dataframe)
    pd.testing.assert_frame_equal(dt._df, sample_dataframe)


def test_add_hour_field(sample_dataframe):
    dt = DatabaseTransformer(sample_dataframe)
    dt.add_field(Field.HOUR)

    # Assert that 'hour' is correctly calculated from 'date'
    assert Field.HOUR in dt.dataframe.columns
    assert (dt.dataframe[Field.HOUR] == sample_dataframe["date"].dt.hour).all()


def test_add_reaction_count_field(sample_dataframe):
    dt = DatabaseTransformer(sample_dataframe)
    dt.add_field(Field.REACTION_COUNT)

    # Assert that 'reaction_count' is calculated correctly from 'reactions'
    assert Field.REACTION_COUNT in dt.dataframe.columns
    expected_reaction_counts = [2, 1, 1, 0, 3]
    assert list(dt.dataframe[Field.REACTION_COUNT]) == expected_reaction_counts


def test_group_by_sum_on_word_count(sample_dataframe):
    dt = DatabaseTransformer(sample_dataframe)
    dt.add_field(Field.AUTHOR).add_field(Field.WORD_COUNT)
    dt.group_by(aggregation=GroupBy.SUM)

    # Assert aggregation grouped by 'author' and summed 'word_count'
    grouped_df = dt.dataframe
    expected_df = pd.DataFrame(
        {"author": ["Alice", "Bob", "John"], "word_count": [35, 20, 20]}
    )
    pd.testing.assert_frame_equal(
        grouped_df.sort_values("author"), expected_df.sort_values("author")
    )


def test_group_by_mean_on_word_count(sample_dataframe):
    dt = DatabaseTransformer(sample_dataframe)
    dt.add_field(Field.AUTHOR).add_field(Field.WORD_COUNT)
    dt.group_by(aggregation=GroupBy.MEAN)

    # Assert aggregation grouped by 'author' and averaged 'word_count'
    grouped_df = dt.dataframe
    expected_df = pd.DataFrame(
        {"author": ["Alice", "Bob", "John"], "word_count": [17.5, 20.0, 10.0]}
    )
    pd.testing.assert_frame_equal(
        grouped_df.sort_values("author"), expected_df.sort_values("author")
    )


def test_filter_min_word_count(sample_dataframe):
    dt = DatabaseTransformer(sample_dataframe)
    dt.add_field(Field.WORD_COUNT)
    dt.filter(filter=Filter.MIN, field=Field.WORD_COUNT, value=15)

    # Assert that only rows with word_count >= 15 are preserved
    filtered_df = dt.dataframe
    assert all(filtered_df["word_count"] >= 15)


def test_filter_equal_author(sample_dataframe):
    dt = DatabaseTransformer(sample_dataframe)
    dt.add_field(Field.AUTHOR)
    dt.filter(filter=Filter.EQUAL, field=Field.AUTHOR, value="Alice")

    # Assert that only rows with author == "Alice" are preserved
    filtered_df = dt.dataframe
    assert all(filtered_df["author"] == "Alice")


def test_sort_by_date(sample_dataframe):
    dt = DatabaseTransformer(sample_dataframe)
    dt.add_field(Field.DATE)
    dt.sort(Field.DATE, ascending=True)

    # Assert that the rows are sorted by date
    sorted_df = dt.dataframe
    assert all(sorted_df["date"].diff().dropna() >= pd.Timedelta(0))


def test_numeric_and_index_cumulative(sample_dataframe):
    dt = DatabaseTransformer(sample_dataframe)

    # First, add a numeric cumulative column for word_count
    dt.cumulative(Field.WORD_COUNT)
    assert "cumulative_word_count" in dt.dataframe.columns
    expected_numeric_cumulative = sample_dataframe["word_count"].cumsum()
    assert list(dt.dataframe["cumulative_word_count"]) == list(
        expected_numeric_cumulative
    )

    # Next, add an index-based cumulative column for author
    dt.cumulative(Field.AUTHOR)
    assert "cumulative_author" in dt.dataframe.columns
    expected_index_cumulative = list(range(1, len(sample_dataframe) + 1))
    assert list(dt.dataframe["cumulative_author"]) == expected_index_cumulative


def test_reset_restores_original_dataframe(sample_dataframe):
    dt = DatabaseTransformer(sample_dataframe)
    dt.add_field(Field.REACTION_COUNT)
    assert Field.REACTION_COUNT in dt.dataframe.columns

    # Reset and verify original DataFrame is restored
    dt.reset()
    pd.testing.assert_frame_equal(dt.dataframe, sample_dataframe)


def test_end_to_end_workflow(sample_dataframe):
    dt = DatabaseTransformer(sample_dataframe)
    dt.filter(Filter.MIN, Field.WORD_COUNT, 15).add_field(Field.AUTHOR).add_field(
        Field.WORD_COUNT
    ).group_by(aggregation=GroupBy.SUM)

    # Assert the resulting DataFrame is as expected
    transformed_df = dt.dataframe
    expected_df = pd.DataFrame(
        {"author": ["Alice", "Bob", "John"], "word_count": [25, 20, 15]}
    )
    pd.testing.assert_frame_equal(transformed_df, expected_df)


def test_invalid_field_error(sample_dataframe):
    dt = DatabaseTransformer(sample_dataframe)

    # Attempting to add an invalid field should raise an error
    with pytest.raises(ValueError):
        dt.add_field("invalid_field")
