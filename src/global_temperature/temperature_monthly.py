from .temperature_base import (
    TemperatureBase,
    TemperatureUnitBase,
    TemperatureQueryResult,
)
from pathlib import Path
import pandas as pd
import logging
from .tools import validate as vd
from collections import OrderedDict
import pygeohash as pgh
import numpy as np
from .config import load_config, PACKAGE_ROOT
import pandera as pa
from pandera import Column, Check


logger = logging.getLogger(__name__)
CONFIG = load_config()


class TemperatureMonthly(TemperatureBase):
    def __init__(
        self,
        search_radius: float = 0.1,
        source_folder: str | Path = "",
        geohash_precision: int = 1,
        max_cache_size: int = 200,
        grid_name: str = "01x01",
    ) -> None:
        """Hold monthly temperature data

        Args:
            search_radius (float, optional): the search radius in degrees to snap to the grid. Defaults to 0.1.
            source_folder (str | Path): the path of the source data folder to read partitioned parquet files. In source folder, it should have a folder structure like this:
                - source_folder / year={year}/ month={month}/{geohash}/data.parquet

            geohash_precision (int, optional): the geohash precision used to partition the data. Defaults to 1.
            max_cache_size (int, optional): the maximum size of monthly data to cache in memory. Defaults to 200.
            grid_name (str, optional): the name of the grid. Defaults to "01x01".
        """
        super().__init__()
        self.search_radius = search_radius

        # set default source folder
        self.source_folder = source_folder
        if not source_folder:
            self.source_folder = PACKAGE_ROOT / CONFIG["default_monthly_data_location"]

        self.geohash_precision = geohash_precision
        self.max_cache_size = max_cache_size

        # create a variable to hold all the monthly temperature data in order
        self.units = OrderedDict()

        self.grid_name = grid_name

        logger.info(
            f"TemperatureMonthly initialized with search_radius={search_radius}, source_folder={self.source_folder}, geohash_precision={geohash_precision}, max_cache_size={max_cache_size}, grid_name={grid_name}"
        )

    def query(
        self,
        year: int,
        month: int,
        latitude: float,
        longitude: float,
        snapped_latitude: float | None = None,
        snapped_longitude: float | None = None,
        geohash: str | None = None,
    ) -> TemperatureQueryResult:
        """
        Query the monthly temperature data based on latitude, longitude and year, month

        Args:
            year (int): The year for which the temperature data is queried.
            month (int): The month for which the temperature data is queried.
            latitude (float): The latitude of the location.
            longitude (float): The longitude of the location.
            snapped_latitude (float | None, optional): Pre-computed snapped latitude on the grid.
                If provided (along with snapped_longitude and geohash), skips snapping computation. Defaults to None.
            snapped_longitude (float | None, optional): Pre-computed snapped longitude on the grid.
                If provided (along with snapped_latitude and geohash), skips snapping computation. Defaults to None.
            geohash (str | None, optional): Pre-computed geohash of the snapped coordinates.
                If provided (along with snapped_latitude and snapped_longitude), skips geohash computation. Defaults to None.

        Returns:
            TemperatureQueryResult: A dictionary containing the following keys:
                - temperature (float): The queried temperature value in Celsius.
                - geohash (str): The geohash of the snapped coordinates.
                - distance (float): The distance between the input and snapped coordinates.
                - snapped_latitude (float): The snapped latitude on the grid.
                - snapped_longitude (float): The snapped longitude on the grid.
        """
        # validate the input parameters such year, month, latitude and longitude
        vd.check_coordinates(latitude, longitude)
        vd.check_year(year)
        vd.check_month(month)

        logger.info(
            f"Querying temperature data for {year}-{month} at {latitude}, {longitude}"
        )

        # Check if snapped coordinates and geohash are provided
        has_snapped_coords = (
            snapped_latitude is not None
            and snapped_longitude is not None
            and geohash is not None
        )

        if has_snapped_coords:
            # Use provided values, skip expensive snapping and geohash computation
            distance = 0.0  # Distance is 0 when using pre-snapped coordinates
            logger.debug(f"Using pre-computed snapped coordinates and geohash")
        else:
            # snap latitude and longitude to the nearest point on the grid
            (snapped_latitude, snapped_longitude), distance = self.snap(
                latitude, longitude, self.grid_name
            )

            if snapped_latitude is None or snapped_longitude is None:
                raise ValueError("Snapped coordinates cannot be None.")

            # Check if the distance is within the search radius
            vd.check_within_radius(self.search_radius, distance)

            # Convert the latitude and longitude to geohash
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
        if snapped_latitude is None or snapped_longitude is None:
            raise ValueError("Snapped coordinates cannot be None.")
        temperature = unit.query(snapped_latitude, snapped_longitude)

        if temperature is None:
            logger.info(f"Temperature data not found for {latitude}, {longitude}")
            temperature = float("-inf")

        return {
            "temperature": round(float(temperature), 2),
            "geohash": str(geohash),
            "distance": float(distance),
            "snapped_latitude": float(snapped_latitude),
            "snapped_longitude": float(snapped_longitude),
        }

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

    def __init__(
        self, source_folder: str | Path, year: int, month: int, geohash: str
    ) -> None:
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
            raise
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
            / "monthly"
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
            # if the file doesn't exist, load from API (not implemented yet)
            # df = self.load_from_remote()

            raise FileNotFoundError(
                f"File {self.filename} does not exist. Please check the file path."
            )
        return df

    def load_from_local(self) -> pd.DataFrame:
        """load data from a file"""
        logger.info(f"Loading data from {self.filename}")
        self.df = pd.read_parquet(self.filename)
        # validate the DataFrame
        self.validate_dataframe(self.df)
        return self.df

    def validate_dataframe(self, df: pd.DataFrame):
        """Validate the DataFrame using pandera."""

        # Define the schema
        schema = pa.DataFrameSchema(
            {
                "date": Column(pa.DateTime, nullable=True),
                "longitude": Column(
                    pa.Float64,
                    checks=[
                        Check.in_range(-180.0, 180.0, error="Longitude out of range")
                    ],
                    nullable=False,
                ),
                "latitude": Column(
                    pa.Float64,
                    checks=[Check.in_range(-90.0, 90.0, error="Latitude out of range")],
                    nullable=False,
                ),
                "temperature_celsius_mean": Column(pa.Float32, nullable=True),
                "geohash_l1": Column(
                    pa.String,
                    # level‑1 geohash is one character
                    Check.str_length(1),
                    nullable=False,
                ),
            },
            # Attempts to coerce dtypes to the defined types if possible
            coerce=False,
        )

        # Validate the DataFrame
        schema.validate(df)

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
            value = filter_data["temperature_celsius_mean"].values[0]

        return value
