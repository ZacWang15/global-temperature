from .temperature import TemperatureBase, TemperatureUnitBase
from pathlib import Path
import pandas as pd
import logging
from .tools import validate as vd
from collections import OrderedDict

logger = logging.getLogger(__name__)


class TemperatureMonthly(TemperatureBase):
    def __init__(
        self,
        search_radius: float = 0.3,
        source_folder: str | Path = "",
        geohash_precision: int = 2,
        max_cache_size: int = 100,
    ) -> None:
        """Hold monthly temperature data

        Args:
            search_radius (float, optional): the search radius in degrees to snap to the grid. Defaults to 0.3.
            source_folder (str | Path): the path of the source data folder to read partitioned parquet files
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

        # create a variable to hold all the monthly temperature data
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
        snapped_latitude, snapped_longitude = self.snap(
            latitude, longitude, self.seaerch_radius
        )
        # Convert the latitude and longitude to geohash, todo
        geohash = self.geohash.encode(snapped_latitude, snapped_longitude, self.geohash_precision)

        # Check if monthly data already loaded before
        if (year, month) not in self.units:
            pass

        # # Check if the DataFrame is loaded
        # if not hasattr(self, "df") or self.df.empty:
        #     logger.warning(
        #         "DataFrame is not loaded or is empty. Please load the data first."
        #     )
        #     self.load()

        # # Check if the year and month are in the DataFrame
        # year_month = f"{year}-{month:02}"
        # if year_month not in self.df.columns:
        #     logger.error(f"Year {year} and month {month} not found in the data.")
        #     return None

        

        # # Check if the latitude and longitude are in the DataFrame
        # if (snapped_latitude, snapped_longitude) not in self.df.index:
        #     logger.error(
        #         f"Snapped oordinates ({snapped_latitude}, {snapped_longitude}) not found in the data."
        #     )
        #     return None

        # # Get the temperature value
        # temperature = self.df.at[(latitude, longitude), year_month]
        # return temperature


class TemperatureMonthlyUnit(TemperatureUnitBase):
    """
    read a single monthly temperature data file
    """

    def __init__(self, file_path: str | Path) -> None:
        """Hold a single monthly temperature data

        Args:
            file_path (str | Path): the path of the source data folder to read a partitioned parquet file
        """
        super().__init__()
        self.file_path = file_path

        # read the data into a pandas dataframe
        self.df = self.load()

    def load(self) -> pd.DataFrame:
        """
        read monthly temperature data from parquet file into a pandas dataframe"
        """
        try:
            if vd.check_file(self.file_path, "parquet"):
                df = pd.read_parquet(self.file_path)

                # check if the dataframe has the required columns
                vd.check_df_columns(
                    df, ["latitude", "longitude", "temperature_celsius_mean"]
                )
        except FileNotFoundError:
            logger.error(f"File not found: {self.file_path}")
            raise
        except pd.errors.EmptyDataError:
            logger.error(f"No data in file: {self.file_path}")

        return df
