import glob
import os
import re

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from utils.logging_setup import get_logger

from .enums import Field

logger = get_logger(__name__)


load_dotenv(override=True)

ENV = os.getenv("ENV", "development")
DATA_PATH = "data/16-2-2025"
CACHE_PATH = ".cache/16-2-2025.parquet"

S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_KEY")
S3_URL = f"s3://{S3_BUCKET}/{S3_KEY}"

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
TIME_ZONE = "Australia/Sydney"
CHANNEL_NAME_REGEX = r".+ - (.+) \["
REACTIONS_REGEX = r"(\w+)\s*\((\d+)\)"
SCENE_END_REGEX = r"\/\s*(?:end\sscene)|(?:scene\send)|(?:SCENESHIFT)"


class DataLoader:
    """DataLoader singleton for loading the dataset."""

    _instance = None
    _df: pd.DataFrame | None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance._df = None
        return cls._instance

    @staticmethod
    def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename columns to snake_case.
        """
        return df.rename(
            columns={
                "AuthorID": Field.AUTHOR_ID,
                "Author": Field.AUTHOR,
                "Date": Field.DATETIME,
                "Content": Field.CONTENT,
                "Attachments": Field.ATTACHMENTS,
                "Reactions": Field.REACTIONS,
            },
        )

    @staticmethod
    def _add_channel_name(df: pd.DataFrame, path: str) -> pd.DataFrame:
        """
        Add a 'channel_name' column.
        """
        filename = os.path.basename(path)
        match = re.search(CHANNEL_NAME_REGEX, filename)

        if match:
            channel_name = match.group(1)
            df[Field.CHANNEL_NAME] = channel_name
        else:
            # Handle the case where no channel name is found
            raise ValueError(f"Could not extract channel name from {filename}")
        return df

    @staticmethod
    def _add_word_count(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add a 'word_count' column.
        """
        word_count = df[Field.CONTENT].str.split().str.len().fillna(0)
        df[Field.WORD_COUNT] = pd.to_numeric(word_count, downcast="integer")
        return df

    @staticmethod
    def _add_scene_end(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add an 'scene_end' column.
        """
        scene_end = df[Field.CONTENT].str.contains(
            SCENE_END_REGEX, case=False, na=False
        )
        df[Field.SCENE_END] = scene_end
        return df

    @staticmethod
    def _reactions_to_dict(reactions: str) -> dict[str, int]:
        """
        Transform a 'reactions' entry into a dictionary of reaction counts.
        """
        if pd.isna(reactions):
            return {}
        return {
            reaction: int(count)
            for reaction, count in re.findall(REACTIONS_REGEX, reactions)
        }

    @staticmethod
    def _process_reactions(df: pd.DataFrame) -> pd.DataFrame:
        """
        Replace the 'reactions' column with a 'reactionCount' column in a DataFrame.
        """
        reactions = df[Field.REACTIONS].apply(DataLoader._reactions_to_dict)
        reaction_count = [max(d.values(), default=0) for d in reactions]
        df[Field.REACTION_COUNT] = pd.to_numeric(reaction_count, downcast="integer")
        return df.drop(Field.REACTIONS, axis=1)

    @staticmethod
    def _process_datetime(df, format=DATE_FORMAT):
        """
        Process the 'datetime' column.
        """
        datetime = pd.to_datetime(
            df[Field.DATETIME], format=format, utc=True
        ).dt.tz_convert(TIME_ZONE)
        df[Field.DATETIME] = datetime
        return df

    @classmethod
    def _read_csv(cls, path: str) -> pd.DataFrame:
        """
        Read a CSV file, return a processed DataFrame.
        """
        df = pd.read_csv(path)
        df = cls._rename_columns(df)
        df = cls._add_word_count(df)
        df = cls._add_channel_name(df, path)
        df = cls._process_reactions(df)
        df = cls._process_datetime(df)
        df = cls._add_scene_end(df)
        return df

    @staticmethod
    def _write_cache(df: pd.DataFrame):
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        df.to_parquet(CACHE_PATH)

    @classmethod
    def _read_csvs(cls) -> pd.DataFrame:
        """
        Read and combine CSVs. If no CSVs were found, return dummy data.
        """
        # Read and combine CSVs
        csv_paths = glob.glob(os.path.join(DATA_PATH, "*.csv"))

        if not csv_paths:
            logger.warning(f"No CSV files found in {DATA_PATH}. Generating dummy data.")
            return cls._generate_dummy_data()

        dfs = [cls._read_csv(path) for path in csv_paths]
        df = pd.concat(dfs, ignore_index=True)

        # https://stackoverflow.com/questions/45639350/retaining-categorical-dtype-upon-dataframe-concatenation
        df[Field.CHANNEL_NAME] = df[Field.CHANNEL_NAME].astype("category")
        df[Field.AUTHOR_ID] = df[Field.AUTHOR_ID].astype("category")
        df[Field.AUTHOR] = df[Field.AUTHOR].astype("category")
        return df

    @classmethod
    def _generate_dummy_data(cls) -> pd.DataFrame:
        num_rows = 500
        authors = ["Aria", "Lyra", "Kaelen", "Solas", "Luna"]
        channels = ["general", "rp-main", "dice-rolls", "lore"]

        # Generate random dates over the last 30 days
        start_date = pd.Timestamp.now(tz=TIME_ZONE) - pd.Timedelta(days=30)
        dates = [
            start_date + pd.Timedelta(seconds=np.random.randint(0, 30 * 24 * 3600))
            for _ in range(num_rows)
        ]

        data = {
            Field.AUTHOR: np.random.choice(authors, num_rows),
            Field.AUTHOR_ID: np.random.choice(
                ["101", "102", "103", "104", "105"], num_rows
            ),
            Field.DATETIME: dates,
            Field.CHANNEL_NAME: np.random.choice(channels, num_rows),
            Field.WORD_COUNT: np.random.randint(5, 200, num_rows),
            Field.REACTION_COUNT: np.random.randint(0, 10, num_rows),
            Field.SCENE_END: np.random.choice([True, False], num_rows, p=[0.05, 0.95]),
            Field.CONTENT: "Dummy message content",
            Field.ATTACHMENTS: "",
        }

        df = pd.DataFrame(data)

        # Ensure data types match expected schema
        df[Field.CHANNEL_NAME] = df[Field.CHANNEL_NAME].astype("category")
        df[Field.AUTHOR_ID] = df[Field.AUTHOR_ID].astype("category")
        df[Field.AUTHOR] = df[Field.AUTHOR].astype("category")
        return df

    def load_cache(self, force: bool = False):
        """
        Load the dataset from a cache. If no cache exists, process raw CSVs and cache the result.
        """
        if not force and os.path.exists(CACHE_PATH):
            logger.info(f"Cache found: Loading from {CACHE_PATH}")
            self._df = pd.read_parquet(CACHE_PATH)
            return self

        # If cache not used, get from raw CSVs
        self._df = self._read_csvs()
        self._write_cache(self._df)
        logger.info(f"Cache written: {CACHE_PATH}")
        return self

    def load_s3(self):
        """
        Load the dataset from Amazon S3.
        """
        logger.info(f"S3 found: Loading from {S3_URL}")
        self._df = pd.read_parquet(S3_URL)
        return self

    def clean(self):
        """
        Remove potentially sensitive data from the dataset.
        """
        if self._df is None:
            return self

        self._df = self._df.drop(
            columns=[Field.AUTHOR_ID, Field.CONTENT, Field.ATTACHMENTS]
        )
        return self

    def load_data(self, force: bool = False, clean: bool = True):
        """
        Load data based on the environment.
        """
        if ENV == "development":
            self.load_cache(force=force)
        elif ENV == "production":
            self.load_s3()
        else:
            raise ValueError(
                f"Invalid ENV value: {ENV}. Choose 'development' or 'production'."
            )

        if clean:
            self.clean()
        return self

    @property
    def df(self) -> pd.DataFrame:
        """
        Return the current DataFrame.
        """
        if self._df is None:
            self.load_data()

        if self._df is None:
            raise RuntimeError("Failed to load data")

        return self._df

    def reset(self):
        """Reset the singleton instance."""
        DataLoader._instance = None


if __name__ == "__main__":
    pd.options.display.max_columns = None  # type: ignore[assignment]
    df = DataLoader().load_cache(force=True).df
    print(df)
