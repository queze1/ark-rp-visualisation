import os
import glob
from platform import processor
import pandas as pd
import re

pd.options.display.max_columns = None

DATA_PATH = "data/23-11-2024"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
TIME_ZONE = "Australia/Sydney"
CHANNEL_NAME_REGEX = r".+ - (.+) \["
REACTIONS_REGEX = r"(\w+)\s*\((\d+)\)"
END_SCENE_REGEX = r"\/\s*(?:end\sscene)|(?:scene\send)|(?:SCENESHIFT)"


class RPProcessor:
    def __init__(self):
        self._data = None

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
        Add a 'channel_name' column to a DataFrame.
        """
        filename = os.path.basename(path)
        channel_name = re.search(CHANNEL_NAME_REGEX, filename).group(1)
        return df.assign(channel_name=channel_name)

    @staticmethod
    def _reactions_to_dict(reactions: str) -> dict[str, int]:
        """
        Transform a 'reactions' entry into a dictionary of reaction counts.
        """
        if pd.isna(reactions):
            return {}
        return {
            reaction: count
            for reaction, count in re.findall(REACTIONS_REGEX, reactions)
        }

    @staticmethod
    def _process_reactions(df: pd.DataFrame) -> pd.DataFrame:
        """
        Process the 'reactions' column in a DataFrame.
        """
        df["reactions"] = df["reactions"].apply(RPProcessor._reactions_to_dict)
        return df

    @staticmethod
    def _process_date(df: pd.DataFrame) -> pd.DataFrame:
        """
        Process the 'date' column in a DataFrame.
        """
        df["date"] = pd.to_datetime(
            df["date"], format=DATE_FORMAT, utc=True
        ).dt.tz_convert(TIME_ZONE)
        return df

    @staticmethod
    def _read_csv(path: str) -> pd.DataFrame:
        """
        Read a CSV file, return a processed DataFrame.
        """
        df = pd.read_csv(path)
        df = RPProcessor._rename_columns(df)
        df = RPProcessor._add_channel_name(df, path)
        df = RPProcessor._process_reactions(df)
        df = RPProcessor._process_date(df)
        return df

    def read_csvs(self):
        """
        Read CSV files, process and concat them.
        """
        csv_paths = glob.glob(os.path.join(DATA_PATH, "*.csv"))
        dfs = [self._read_csv(path) for path in csv_paths]
        self._data = pd.concat(dfs, ignore_index=True)

    def add_scene_id(self):
        """
        Add a 'sceneID' column to a DataFrame.
        """

        # TODO: Handle scene messages not being contiguous.
        end_scene = self._data["content"].str.contains(
            END_SCENE_REGEX, case=False, na=False
        )
        scene_id = end_scene.shift(1).fillna(0).cumsum()
        self._data = self._data.assign(sceneId=scene_id)

    @property
    def data(self) -> pd.DataFrame | None:
        if self._data is None:
            raise ValueError("Data has not been read yet!")
        return self._data


if __name__ == "__main__":
    processor = RPProcessor()
    processor.read_csvs()
    processor.add_scene_id()

    print(processor.data)
