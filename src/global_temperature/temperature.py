from abc import ABC, abstractmethod
from .temperature_monthly import TemperatureMonthly
from .temperature_daily import TemperatureDaily
import logging

logger = logging.getLogger(__name__)


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

    def snap(self, latitude: float, longitude: float) -> tuple[float, float]:
        """
        Snap the latitude and longitude to the nearest grid point.
        """
        # first check if the coordinates are valid
        self.check_coordinates(latitude, longitude)

        # snap to the nearest grid point
        snapped_latitude = round(latitude * 100) / 100
        snapped_longitude = round(longitude * 100) / 100
        return snapped_latitude, snapped_longitude




class TemperatureUnitBase(ABC):
    """
    Abstract base class for a temperature data unit.
    """

    @abstractmethod
    def load(self):
        """Abstract method that subclasses must implement."""
        pass
