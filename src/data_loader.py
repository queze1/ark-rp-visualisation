import glob
import os
import re

import boto3
import pandas as pd
from dotenv import load_dotenv

from enums import Field
from logging_setup import get_logger

logger = get_logger(__name__)


load_dotenv(override=True)

ENV = os.getenv("ENV", "development")
DATA_PATH = "data/16-2-2025"
CACHE_PATH = ".cache/16-2-2025.pkl"
S3_PATH = dict(Bucket=os.getenv("S3_BUCKET"), Key="16-2-2025.pkl")

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
TIME_ZONE = "Australia/Sydney"
CHANNEL_NAME_REGEX = r".+ - (.+) \["
REACTIONS_REGEX = r"(\w+)\s*\((\d+)\)"
SCENE_END_REGEX = r"\/\s*(?:end\sscene)|(?:scene\send)|(?:SCENESHIFT)"


class DataLoader:
    """DataLoader singleton for loading the dataset."""

    _instance = None
    _df: pd.DataFrame

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
        Process the 'reactions' column and add a 'reactionCount' column to a DataFrame.
        """
        reactions = df["reactions"].apply(DataLoader._reactions_to_dict)
        reaction_count = [max(d.values(), default=0) for d in reactions]
        df[Field.REACTIONS] = reactions
        df[Field.REACTION_COUNT] = pd.to_numeric(reaction_count, downcast="integer")
        return df

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
    def _write_cache(df):
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        df.to_pickle(CACHE_PATH)

    @classmethod
    def _read_csvs(cls):
        # Read and combine CSVs
        csv_paths = glob.glob(os.path.join(DATA_PATH, "*.csv"))
        dfs = [cls._read_csv(path) for path in csv_paths]
        df = pd.concat(dfs, ignore_index=True)

        # https://stackoverflow.com/questions/45639350/retaining-categorical-dtype-upon-dataframe-concatenation
        df[Field.CHANNEL_NAME] = df[Field.CHANNEL_NAME].astype("category")
        df[Field.AUTHOR_ID] = df[Field.AUTHOR_ID].astype("category")
        df[Field.AUTHOR] = df[Field.AUTHOR].astype("category")
        return df

    def load_pickle(self, force: bool = False):
        """
        Load the dataset from a pickle cache. If no cache exists, process raw CSVs and cache the result.
        """
        if not force and os.path.exists(CACHE_PATH):
            logger.info(f"Cache found: Loading from {CACHE_PATH}")
            self._df = pd.read_pickle(CACHE_PATH)
            return self

        # If cache not used, get from raw CSVs
        self._df = self._read_csvs()
        self._write_cache(self._df)
        logger.info(f"Cache written: {CACHE_PATH}")
        return self

    def load_s3(self):
        """
        Load the dataset from a S3 object.
        """
        s3 = boto3.client("s3")
        with s3.get_object(**S3_PATH)["Body"] as response:
            self._df = pd.read_pickle(response)

        logger.info(f"S3 found: Loading from {S3_PATH['Bucket']}/{S3_PATH['Key']}")
        return self

    def clean(self):
        """
        Remove potentially sensitive data from the dataset.
        """
        self._df = self._df.drop(
            columns=[Field.AUTHOR_ID, Field.CONTENT, Field.ATTACHMENTS]
        )
        return self

    def load_data(self, force: bool = False, clean: bool = True):
        """
        Loads data based on the environment.
        """
        if ENV == "development":
            self.load_pickle(force=force)
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
        return self._df

    def reset(self):
        """Reset the singleton instance."""
        DataLoader._instance = None


if __name__ == "__main__":
    pd.options.display.max_columns = None  # type: ignore[assignment]
    df = DataLoader().load_pickle(force=True).df
    print(df)
