from .temperature_base import TemperatureBase, TemperatureUnitBase
from pathlib import Path
import pandas as pd
import logging
from .tools import validate as vd
from collections import OrderedDict
import pygeohash as pgh
import numpy as np


logger = logging.getLogger(__name__)


class TemperatureMonthly(TemperatureBase):
    def __init__(
        self,
        search_radius: float = 0.3,
        source_folder: str | Path = "",
        geohash_precision: int = 2,
        max_cache_size: int = 200,
    ) -> None:
        """Hold monthly temperature data

        Args:
            search_radius (float, optional): the search radius in degrees to snap to the grid. Defaults to 0.3.
            source_folder (str | Path): the path of the source data folder to read partitioned parquet files. In source folder, it should have a folder structure like this:
                - source_folder / year={year}/ month={month}/{geohash}/data.parquet

            geohash_precision (int, optional): the geohash precision used to partition the data. Defaults to 2.
            max_cache_size (int, optional): the maximum size of monthly data to cache. Defaults to 100.
        """
        super().__init__()
        self.search_radius = search_radius

        # set default source folder
        self.source_folder = source_folder
        if not source_folder:
            self.source_folder = Path(__file__).parent / "data" / "monthly"

        self.geohash_precision = geohash_precision
        self.max_cache_size = max_cache_size

        # create a variable to hold all the monthly temperature data in order
        self.units = OrderedDict()

    def query(
        self,
        year: int,
        month: int,
        latitude: float,
        longitude: float,
    ) -> float | None:
        """
        Query the monthly temperature data based on latitude, longitude and year, month
        """
        # validate the input parameters such year, month, latitude and longitude
        vd.check_coordinates(latitude, longitude)
        vd.check_year(year)
        vd.check_month(month)

        # snap latitude and longitude to the nearest point on the grid, todo
        (snapped_latitude, snapped_longitude), distance = self.snap(latitude, longitude)

        # Check if the distance is within the search radius
        vd.check_within_radius(self.search_radius, distance)

        # Convert the latitude and longitude to geohash, todo
        geohash = pgh.encode(
            snapped_latitude, snapped_longitude, self.geohash_precision
        )

        # Check if monthly data already loaded before
        if (year, month, geohash) not in self.units:
            # load the monthly data
            unit = TemperatureMonthlyUnit(self.source_folder, year, month, geohash)
            self.units[(year, month, geohash)] = unit
        else:
            unit = self.units[(year, month, geohash)]

        # query the temperature data from unit
        temperature = unit.query(snapped_latitude, snapped_longitude)

        if temperature is None:
            logger.info(f"Temperature data not found for {latitude}, {longitude}")
            return None
        return temperature

    def add_unit(
        self,
        year: int,
        month: int,
        geohash: str,
        unit: TemperatureUnitBase,
    ) -> None:
        """add a unit to self.units to hold TemperatureMonthlyUnit instances"""
        if len(self.units) >= self.max_cache_size:
            # remove the oldest unit
            self.units.popitem(last=False)
        self.units[(year, month, geohash)] = unit


class TemperatureMonthlyUnit(TemperatureUnitBase):
    """
    read a single monthly temperature data file
    """

    def __init__(self, source_folder: str, year: int, month: int, geohash: str) -> None:
        super().__init__()
        self.source_folder = source_folder
        self.year = year
        self.month = month
        self.geohash = geohash

        self.filename = self.build_filename()

        # check if file format if valid
        vd.check_file_format(self.filename)

        # check if file exists
        try:
            vd.check_file_exists(self.filename)
        except FileNotFoundError:
            self.file_exist = False
        else:
            self.file_exist = True

    @property
    def data(self) -> pd.DataFrame:
        """Property to get the DataFrame, loading it if necessary."""
        if not hasattr(self, "_data"):
            self._data = self.load()
        return self._data

    def build_filename(self) -> Path:
        """build the filename"""
        # build the filename
        self.filename = (
            Path(self.source_folder)
            / f"year={self.year}"
            / f"month={self.month}"
            / f"geohash={self.geohash}"
            / "data.parquet"
        )
        return self.filename

    def load(self) -> pd.DataFrame:
        """load the data"""
        if self.file_exist:
            df = self.load_from_local()
        else:
            df = self.load_from_remote()
        return df

    def load_from_local(self) -> pd.DataFrame:
        """load data from a file"""
        logger.info(f"Loading data from {self.filename}")
        self.df = pd.read_parquet(self.filename)
        return self.df

    def load_from_remote(self):
        """load data from an API"""
        raise NotImplementedError(
            f"{self.__class__.__name__} doesn't implement {self.load_from_remote.__name__} method"
        )

    def query(self, latitude: float, longitude: float) -> float | None:
        """query the temperature value"""
        # validate the input parameters such latitude and longitude
        vd.check_coordinates(latitude, longitude)

        # Check if the DataFrame is loaded
        if not hasattr(self, "_data") or self._data.empty:
            self._data = self.load()

        tolerance = 1e-2
        lat_close = np.isclose(self._data["latitude"], latitude, atol=tolerance)
        lon_close = np.isclose(self._data["longitude"], longitude, atol=tolerance)

        filter_data = self._data[lat_close & lon_close]
        if filter_data.empty:
            logger.info(f"Temperature data not found for {latitude}, {longitude}")
            return None
        else:
            # get the temperature value
            value = round(filter_data["temperature_celsius_mean"].values[0], 2)

        return value
