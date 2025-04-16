from abc import ABC, abstractmethod
from .temperature_monthly import TemperatureMonthly
from .temperature_daily import TemperatureDaily
import logging
from .grids.grid import Grids
from .config import load_config, PACKAGE_ROOT
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)
config = load_config("src/global_temperature/config.yaml")


class TemperatureFactory:
    def __init__(self):
        self._builders = {"monthly": TemperatureMonthly, "daily": TemperatureDaily}

    def create(self, data_type: str, *args, **kwargs):
        if data_type not in self._builders:
            raise ValueError(f"Unknown data_type: {data_type}")
        return self._builders[data_type](*args, **kwargs)


class TemperatureBase(ABC):
    """
    Abstract base class for temperature data.
    """

    @abstractmethod
    def query(self):
        """Abstract method that subclasses must implement."""
        pass

    def snap(self, latitude: float, longitude: float) -> tuple[np.ndarray, float]:
        """
        Snap the latitude and longitude to the nearest grid point.
        """
        # first check if the coordinates are valid
        self.check_coordinates(latitude, longitude)

        # create a grid instance
        grid = Grids()
        grid.load_grid(
            (PACKAGE_ROOT / config["grids"]["default_grid_file"]).resolve(),
            config["grids"]["default_grid_name"],
        )

        # snap to the nearest grid point
        point, distance = grid.query(
            config["grids"]["default_grid_name"], latitude, longitude
        )
        return point, distance


class TemperatureUnitBase(ABC):
    """
    Abstract base class for a temperature data unit.
    """

    @abstractmethod
    def load(self):
        """Abstract method that subclasses must implement."""
        pass
