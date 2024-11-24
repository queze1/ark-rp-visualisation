import os
import glob
import pandas as pd
import re
import ast

pd.options.display.max_columns = None

DATA_PATH = "data/23-11-2024"
CACHE_PATH = "data/cache/23-11-2024.csv"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
TIME_ZONE = "Australia/Sydney"
CHANNEL_NAME_REGEX = r".+ - (.+) \["
REACTIONS_REGEX = r"(\w+)\s*\((\d+)\)"
END_SCENE_REGEX = r"\/\s*(?:end\sscene)|(?:scene\send)|(?:SCENESHIFT)"


class DataLoader:
    def __init__(self):
        self._df = None

    @staticmethod
    def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Rename columns of a DataFrame to snake_case.
        """
        return df.rename(
            columns={
                "AuthorID": "authorId",
                "Author": "author",
                "Date": "date",
                "Content": "content",
                "Attachments": "attachments",
                "Reactions": "reactions",
            },
        )

    @staticmethod
    def _add_channel_name(df: pd.DataFrame, path: str) -> pd.DataFrame:
        """
        Add a 'channelName' column to a DataFrame.
        """
        filename = os.path.basename(path)
        channel_name = re.search(CHANNEL_NAME_REGEX, filename).group(1)
        return df.assign(channelName=channel_name)

    @staticmethod
    def _add_word_count(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add a 'wordCount' column to a DataFrame.
        """
        word_count = df["content"].str.split().str.len().fillna(0)
        return df.assign(wordCount=word_count)

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
        df["reactions"] = df["reactions"].apply(DataLoader._reactions_to_dict)
        df["reactionCount"] = [max(d.values(), default=0) for d in df["reactions"]]
        return df

    @staticmethod
    def _process_date(df: pd.DataFrame, format=DATE_FORMAT) -> pd.DataFrame:
        """
        Process the 'date' column in a DataFrame.
        """
        df["date"] = pd.to_datetime(df["date"], format=format, utc=True).dt.tz_convert(
            TIME_ZONE
        )
        return df

    @staticmethod
    def _read_csv(path: str) -> pd.DataFrame:
        """
        Read a CSV file, return a processed DataFrame.
        """
        df = pd.read_csv(path)
        df = DataLoader._rename_columns(df)
        df = DataLoader._add_word_count(df)
        df = DataLoader._add_channel_name(df, path)
        df = DataLoader._process_reactions(df)
        df = DataLoader._process_date(df)
        return df

    def _read_cache(self):
        self._df = pd.read_csv(CACHE_PATH)
        # Unstringify date and reactions
        self._df = self._process_date(self._df, format="ISO8601")
        self._df["reactions"] = self._df["reactions"].apply(ast.literal_eval)
        return self

    def _write_cache(self):
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        self._df.to_csv(CACHE_PATH, index=False)

    def read_csvs(self, force: bool = False):
        """
        Read CSV files, process and cache them.
        """
        if not force and os.path.exists(CACHE_PATH):
            print(f"Cache found: Loading from {CACHE_PATH}")
            return self._read_cache()

        # If cache not used, process all files
        csv_paths = glob.glob(os.path.join(DATA_PATH, "*.csv"))
        dfs = [self._read_csv(path) for path in csv_paths]
        self._df = pd.concat(dfs, ignore_index=True)

        self._write_cache()
        print(f"Cache written: {CACHE_PATH}")
        return self

    def add_scene_id(self):
        """
        Add a 'sceneID' column to a DataFrame.
        """
        # TODO: Handle scene messages not being contiguous.
        end_scene = self._df["content"].str.contains(
            END_SCENE_REGEX, case=False, na=False
        )
        scene_id = end_scene.shift(1).fillna(0).cumsum()
        self._df = self._df.assign(sceneId=scene_id)
        return self

    @property
    def df(self) -> pd.DataFrame:
        """
        Return the current DataFrame.
        """
        if self._df is None:
            raise ValueError("Data has not been read yet")
        return self._df

    def load_data(self, force: bool = False):
        """
        Helper to to build a clean dataset.
        """
        return self.read_csvs(force=force).add_scene_id()


if __name__ == "__main__":
    df = DataLoader().load_data(force=False).df
    print(df)
