import pandas as pd
import pytest
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_integer_dtype,
    is_object_dtype,
)
from pandas.testing import assert_frame_equal

from core import DataLoader
from core.enums import Field


def is_categorical_dtype(column):
    return isinstance(column.dtype, pd.CategoricalDtype)


DTYPES = {
    Field.AUTHOR: is_categorical_dtype,
    Field.DATETIME: is_datetime64_any_dtype,
    Field.REACTIONS: is_object_dtype,
    Field.WORD_COUNT: is_integer_dtype,
    Field.CHANNEL_NAME: is_categorical_dtype,
    Field.REACTION_COUNT: is_integer_dtype,
    Field.SCENE_END: is_bool_dtype,
}


@pytest.fixture(scope="session")
def data_loader():
    loader = DataLoader()
    yield loader
    loader.reset()


@pytest.fixture(scope="session")
def load_data_nocache(data_loader):
    """Loads data without caching."""
    return data_loader.load_pickle(force=True).clean().df


@pytest.fixture(scope="session")
def load_data_cache(data_loader):
    """Loads data with caching."""
    return data_loader.load_pickle().clean().df


@pytest.fixture(scope="session")
def load_data_s3(data_loader):
    """Loads data from S3."""
    return data_loader.load_s3().clean().df


@pytest.fixture(
    params=[
        pytest.param("load_data_nocache", marks=pytest.mark.local),
        pytest.param("load_data_cache", marks=pytest.mark.local),
        "load_data_s3",
    ],
    scope="session",
)
def load_data(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(
    params=[
        "load_data_cache",
        "load_data_s3",
    ],
    scope="session",
)
def load_data_other(request):
    return request.getfixturevalue(request.param)


def test_nocache_column_keys_and_dtypes(load_data):
    """
    Test that the DataFrame matches the required columns
    and the dtype of each column satisfies the associated functions.
    """

    df = load_data

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


def test_nocache_missing_values(load_data):
    """
    Test that the DataFrame contains no missing values.
    """
    df = load_data
    columns_with_na = df.columns[df.isna().any()].tolist()

    assert not columns_with_na, (
        f"The following columns have missing values: {columns_with_na}"
    )


@pytest.mark.local
def test_equal(load_data_nocache, load_data_other):
    """
    Test that the DataFrame loaded with force=True matches the other DataFrames.
    """
    df_nocache = load_data_nocache
    df_other = load_data_other

    assert_frame_equal(df_nocache, df_other, check_dtype=True)
