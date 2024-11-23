import os
import glob
from platform import processor
import pandas as pd

pd.options.display.max_columns = None
DATA_PATH = "data/23-11-2024"


class RPProcessor:
    def __init__(self):
        self._data = None

    def read_csv(self):
        csv_paths = glob.glob(os.path.join(DATA_PATH, "*.csv"))
        dfs = [pd.read_csv(path) for path in csv_paths]
        self._data = pd.concat(dfs, ignore_index=True)

    @property
    def data(self):
        if self._data is None:
            raise ValueError("Data has not been read yet!")
        return self._data


if __name__ == "__main__":
    processor = RPProcessor()
    processor.read_csv()

    print(processor.data)
