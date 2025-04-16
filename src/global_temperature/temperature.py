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
