import pytest
from pandas.api.types import (
    is_any_real_numeric_dtype,
    is_datetime64_any_dtype,
    is_object_dtype,
    is_bool_dtype,
    is_integer_dtype,
)
from pandas.testing import assert_frame_equal

from enums import Field
from data_loader import DataLoader

DTYPES = {
    Field.AUTHOR: is_object_dtype,
    Field.DATETIME: is_datetime64_any_dtype,
    Field.REACTIONS: is_object_dtype,
    Field.WORD_COUNT: is_any_real_numeric_dtype,
    Field.CHANNEL_NAME: is_object_dtype,
    Field.REACTION_COUNT: is_integer_dtype,
    Field.SCENE_END: is_bool_dtype,
}


@pytest.fixture(scope="session")
def load_data_nocache():
    """
    Fixture to load the DataFrame.
    """
    return DataLoader().load_csv(force=True).clean().df


@pytest.fixture(scope="session")
def load_data_cache():
    """
    Fixture to load the cached DataFrame.
    """
    return DataLoader().load_csv().clean().df


@pytest.fixture(scope="session")
def load_data_s3():
    """
    Fixture to load the remote DataFrame.
    """
    return DataLoader().load_s3().clean().df


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

    assert not columns_with_na, (
        f"The following columns have missing values: {columns_with_na}"
    )


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


def test_s3_equal(load_data_nocache, load_data_s3):
    """
    Test that the DataFrame loaded with force=True matches the remote DataFrame.
    """
    df_nocache = load_data_nocache
    df_s3 = load_data_s3

    (
        assert_frame_equal(df_nocache, df_s3, check_dtype=True),
        "Remote DataFrame and uncached DataFrame are not equal.",
    )
