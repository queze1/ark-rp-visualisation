import ast
import glob
import os
import re

import boto3
import pandas as pd
from dotenv import load_dotenv

from logging_setup import get_logger

logger = get_logger(__name__)


load_dotenv(override=True)

ENV = os.getenv("ENV", "development")
DATA_PATH = "data/25-12-2024"
CACHE_PATH = ".cache/25-12-2024.csv"
S3_PATH = dict(Bucket=os.getenv("S3_BUCKET"), Key="25-12-2024.csv")

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
TIME_ZONE = "Australia/Sydney"
CHANNEL_NAME_REGEX = r".+ - (.+) \["
REACTIONS_REGEX = r"(\w+)\s*\((\d+)\)"
SCENE_END_REGEX = r"\/\s*(?:end\sscene)|(?:scene\send)|(?:SCENESHIFT)"


class DataLoader:
    def __init__(self):
        self._df = None

    @staticmethod
    def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename columns to snake_case.
        """
        return df.rename(
            columns={
                "AuthorID": "author_id",
                "Author": "author",
                "Date": "datetime",
                "Content": "content",
                "Attachments": "attachments",
                "Reactions": "reactions",
            },
        )

    @staticmethod
    def _add_channel_name(df: pd.DataFrame, path: str) -> pd.DataFrame:
        """
        Add a 'channel_name' column.
        """
        filename = os.path.basename(path)
        channel_name = re.search(CHANNEL_NAME_REGEX, filename).group(1)
        return df.assign(channel_name=channel_name)

    @staticmethod
    def _add_word_count(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add a 'word_count' column.
        """
        word_count = df["content"].str.split().str.len().fillna(0)
        return df.assign(word_count=word_count)

    @staticmethod
    def _add_scene_end(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add an 'scene_end' column.
        """
        scene_end = df["content"].str.contains(SCENE_END_REGEX, case=False, na=False)
        return df.assign(scene_end=scene_end)

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
        return df.assign(reactions=reactions, reaction_count=reaction_count)

    @staticmethod
    def _process_datetime(df, format=DATE_FORMAT):
        """
        Process the 'datetime' column.
        """
        datetime = pd.to_datetime(
            df["datetime"], format=format, utc=True
        ).dt.tz_convert(TIME_ZONE)
        return df.assign(datetime=datetime)

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

    @classmethod
    def _process_cache(cls, df):
        # Unstringify datetime and reactions
        df = cls._process_datetime(df, format="ISO8601")
        df = df.assign(reactions=df["reactions"].apply(ast.literal_eval))
        return df

    @staticmethod
    def _write_cache(df):
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        df.to_csv(CACHE_PATH, index=False)

    def load_csv(self, force: bool = False):
        """
        Load the dataset from a CSV cache. If no cache exists, process CSV files and cache them.
        """
        if not force and os.path.exists(CACHE_PATH):
            logger.info(f"Cache found: Loading from {CACHE_PATH}")
            self._df = pd.read_csv(CACHE_PATH)
            self._df = self._process_cache(self._df)
            return self

        # If cache not used, process all files
        csv_paths = glob.glob(os.path.join(DATA_PATH, "*.csv"))
        dfs = [self._read_csv(path) for path in csv_paths]
        self._df = pd.concat(dfs, ignore_index=True)
        self._write_cache(self._df)

        logger.info(f"Cache written: {CACHE_PATH}")
        return self

    def load_s3(self):
        """
        Load the dataset from a S3 object.
        """
        s3 = boto3.client("s3")
        with s3.get_object(**S3_PATH)["Body"] as response:
            self._df = pd.read_csv(response)
            self._df = self._process_cache(self._df)

        logger.info(f"S3 found: Loading from {S3_PATH['Bucket']}/{S3_PATH['Key']}")
        return self

    def clean(self):
        """
        Remove potentially sensitive data from the dataset.
        """
        self._df = self._df.drop(columns=["author_id", "content", "attachments"])
        return self

    @property
    def df(self) -> pd.DataFrame:
        """
        Return the current DataFrame.
        """
        if self._df is None:
            raise ValueError("Data has not been read yet")
        return self._df


df = None

if __name__ == "__main__":
    pd.options.display.max_columns = None
    df = DataLoader().load_csv(force=True).df

elif df is None:
    # Initialise singleton
    if ENV == "development":
        df = DataLoader().load_csv().clean().df
    elif ENV == "production":
        df = DataLoader().load_s3().clean().df
