import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from pathlib import Path


class SingletonMeta(type):
    """
    A metaclass for creating singleton classes.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Grids(metaclass=SingletonMeta):
    """
    Load and manage grid data.
    """

    def __init__(self):
        self.grids = {}

    def load_grid(self, file: str | Path, grid_name: str) -> None:
        """
        Load grid data from a file.
        """
        # Check if the file exists
        if not Path(file).exists():
            raise FileNotFoundError(f"File {file} does not exist.")

        # Load the grid data
        df = pd.read_parquet(file)

        # Extract coordinate points as a NumPy array.
        points = df[["latitude", "longitude"]].values

        # Build KDTree for fast nearest-neighbor lookup.
        tree = cKDTree(points)

        self.grids[grid_name] = tree

    def query(
        self, grid_name: str, latitude: float, longitude: float
    ) -> tuple[np.ndarray, float]:
        """
        Query the grid for the nearest point to the given latitude and longitude.

        Returns the coordinates of the nearest point and the distance to it.
        """
        if grid_name not in self.grids:
            raise ValueError(f"Grid {grid_name} not loaded.")

        # Get the KDTree for the specified grid.
        tree = self.grids[grid_name]

        # Query the nearest point.
        distance, index = tree.query([latitude, longitude])

        # Convert the distance to np.float32 and return the coordinates of the nearest point.
        return np.round(tree.data[index], decimals=1).astype(np.float32), np.float32(
            distance
        )
