from src.plot.data_loader import DataLoader
from pandas.api.types import (
    is_object_dtype,
    is_datetime64_any_dtype,
    is_any_real_numeric_dtype,
)
from pandas.testing import assert_frame_equal
import pytest

DTYPES = {
    "author": is_object_dtype,
    "date": is_datetime64_any_dtype,
    "reactions": is_object_dtype,
    "word_count": is_any_real_numeric_dtype,
    "channel_name": is_object_dtype,
    "sceneId": is_object_dtype,
}


@pytest.fixture(scope="session")
def load_data_nocache():
    """
    Fixture to load the DataFrame.
    """
    return DataLoader().load_data(force=True).df


@pytest.fixture(scope="session")
def load_data_cache():
    """
    Fixture to load the cached DataFrame.
    """
    return DataLoader().load_data().df


def test_nocache_column_keys_and_dtypes(load_data_nocache):
    """
    Test that the DataFrame matches the required columns
    and the dtype of each column satisfies the associated functions.
    """

    df = load_data_nocache

    # Assert that the DataFrame has the exact expected columns
    assert set(df.columns) == set(DTYPES.keys()), (
        f"DataFrame columns do not match expected columns. "
        f"Expected: {set(DTYPES.keys())}, Found: {set(df.columns)}"
    )

    # Check the dtype validation function for each column
    for column, dtype_check in DTYPES.items():
        assert dtype_check(df[column]), (
            f"Column '{column}' does not satisfy its dtype validation. "
            f"Expected dtype check: {dtype_check}, Found dtype: {df[column].dtype}"
        )


def test_nocache_missing_values(load_data_nocache):
    """
    Test that the DataFrame contains no missing values.
    """
    df = load_data_nocache
    columns_with_na = df.columns[df.isna().any()].tolist()

    assert (
        not columns_with_na
    ), f"The following columns have missing values: {columns_with_na}"


def test_cache_equal(load_data_nocache, load_data_cache):
    """
    Test that the DataFrame loaded with force=True matches the cached DataFrame.
    """
    df_nocache = load_data_nocache
    df_cache = load_data_cache

    (
        assert_frame_equal(df_nocache, df_cache, check_dtype=True),
        "Cached DataFrame and uncached DataFrame are not equal.",
    )
