from global_temperature.tools.download import download

# 1. Download the data. The available range of years is from 1990 to 2025.
# This is not an API service, so please don't abuse the API. If possible, please download the data only once.

# specify a path where you want to download the data. An absolute path is recommended.
target_path = "examples/data"

# Method1: download the data for a specific year range (both inclusive)
# start_year = 2023
# end_year = 2024

# the function will download the data from the API and returnes the years that failed to download
# failed_years = download(
#     start_year=start_year,
#     end_year=end_year,
#     target_path=target_path,
#     # delete_archived_files=False,  # if you want to keep the zipped files
# )

# Method2: you can specify the years that you want to download
years = [2020, 2022, 2025]
failed_years = download(years=years, target_path=target_path)
if failed_years:
    raise Exception(
        f"Failed to download the following years: {', '.join(map(str, failed_years))}"
    )

# 2. After downloading the file, you can query any locations globally (only land areas are supported)
# The tool will automatically find the nearest grid point to the specified location and return the temperature data.
import global_temperature as gt

temperature_monthly = gt.TemperatureFactory.create_temperature_object(
    data_type="monthly",
    # specify the folder that you downloaded the data (if possible, use abosolute path)
    source_folder=target_path,
    # specify search radius in degrees, the default is 0.1 degrees
    # this means the tool will find the nearest grid point within 0.1 degrees. You can increase the value to get a larger search radius.
    search_radius=0.1,
)

# Query the temperature for a specific year, month, latitude, and longitude
year = 2025
month = 4
latitude = -38.2551
longitude = 145.2414
temp = temperature_monthly.query(year, month, latitude, longitude)
print(
    f"Temperature in {year}-{month} at ({latitude}, {longitude}): {temp['temperature']} °C"
)
print(temp)


# 3. When there is not grid point within the search radius, the tool will raise an exception.
# You can catch the exception and handle it as you like.
from global_temperature.errors import NoNearbyPointError

try:
    # Query a location which is in the ocean
    year = 2025
    month = 4
    latitude = -38.1235
    longitude = 144.9779
    temp = temperature_monthly.query(year, month, latitude, longitude)
    print(
        f"Temperature in {year}-{month} at ({latitude}, {longitude}): {temp['temperature']} °C"
    )
except NoNearbyPointError as e:
    print(f"No nearby point found: {e}")
