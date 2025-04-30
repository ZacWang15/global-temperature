from abc import ABC, abstractmethod
from .grids.grid import Grids
from .config import load_config, PACKAGE_ROOT
from pathlib import Path
import numpy as np
import logging


CONFIG = load_config()
logger = logging.getLogger(__name__)


class TemperatureBase(ABC):
    """
    Abstract base class for temperature data.
    """

    @abstractmethod
    def query(self):
        """Abstract method that subclasses must implement."""
        pass

    def snap(
        self, latitude: float, longitude: float, grid_name: str = "03x03"
    ) -> tuple[np.ndarray, float]:
        """
        Snap the latitude and longitude to the nearest grid point.
        """
        # create a grid instance
        grid = Grids()
        grid.load_grid(
            (PACKAGE_ROOT / CONFIG["grids"][grid_name]["grid_file"]).resolve(),
            CONFIG["grids"][grid_name]["grid_name"],
        )

        # snap to the nearest grid point
        point, distance = grid.query(
            CONFIG["grids"][grid_name]["grid_name"], latitude, longitude
        )
        return point, distance


class TemperatureUnitBase(ABC):
    """
    Abstract base class for a temperature data unit.
    """

    @property
    @abstractmethod
    def data(self):
        """Abstract property that subclasses must implement."""
        pass

    @abstractmethod
    def load(self):
        """Abstract method that subclasses must implement."""
        pass
