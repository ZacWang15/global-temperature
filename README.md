# Global Temperature

This project provides average monthly temperature (celsius degree) globally in land area by 0.1 degree x 0.1 degree grids.

The data is at monthly interval from 1970 till now and dataset will update every month for the current year.

The tool can match a latitude, longitude point to the nearest point in the grid and return the celsius degree according to year, month you pass to it.

## Converage
The yellow area in the [photo](https://global-temperature.com/coverage.png) is the coverage of the project.


## Install
Require Python >= 3.10
> pip install global-temperature

## How to use

You can also find usage examples in the [`examples.py`](examples.py) file.

### Usage Examples

#### 1. Download Temperature Data

First, download the temperature data for the years you need. The available range is from 1970 to 2025.

```python
from global_temperature.tools.download import download

# Specify a path where you want to download the data (absolute path recommended)
target_path = "data"

# Method 1: Download data for a specific year range (both inclusive)
start_year = 2023
end_year = 2024
failed_years = download(
    start_year=start_year,
    end_year=end_year,
    target_path=target_path,
    # delete_archived_files=False,  # Keep zipped files if needed
)

# Method 2: Download specific years
years = [2020, 2022, 2025]
failed_years = download(years=years, target_path=target_path)

if failed_years:
    print(f"Failed to download: {', '.join(map(str, failed_years))}")
```

#### 2. Query Temperature Data

After downloading, you can query temperature data for any location globally (land areas only).

```python
import global_temperature as gt

# Create a temperature object. You only need to create it once.
temperature_monthly = gt.TemperatureFactory.create_temperature_object(
    data_type="monthly",
    source_folder=target_path,  # Path where you downloaded the data
    search_radius=0.1,          # Search radius in degrees (default: 0.1)
    max_cache_size=200          # Maximum number of data partitions to keep in memory cache
)

# Query temperature for a specific location and time
year = 2025
month = 4
latitude = -38.2551   # Melbourne, Australia
longitude = 145.2414

temp = temperature_monthly.query(year, month, latitude, longitude)
print(f"Temperature in {year}-{month} at ({latitude}, {longitude}): {temp['temperature']} °C")
# Output: Temperature in 2025-4 at (-38.2551, 145.2414): 17.17852783203125 °C
```

### Key Parameters of create_temperature_object()

- **search_radius**: Maximum distance (in degrees) to search for the nearest grid point
- **data_type**: Currently supports "monthly" for monthly temperature data
- **source_folder**: Directory containing the downloaded temperature data files
- **max_cache_size**: Maximum number of data partitions to keep in memory cache. Each partition represents one year/month/geohash combination.

### 3. Understanding the Response

The query method returns a dictionary with detailed information:

```python
print(temp)
# Output:
# {
#     'temperature': np.float32(17.178528),      # Temperature in Celsius
#     'geohash': 'r',                            # Geohash of nearest grid point as the data is partitioned by year, month, geohash
#     'distance': np.float32(0.061073482),       # Distance to grid point (degrees)
#     'snapped_latitude': np.float32(-38.3),     # Latitude of nearest grid point
#     'snapped_longitude': np.float32(145.2)     # Longitude of nearest grid point
# }
```

### 4. Error Handling

When no grid point exists within the search radius, an exception is raised:

```python
from global_temperature.errors import NoNearbyPointError

try:
    # Query a location in the ocean (no nearby land point)
    temp = temperature_monthly.query(2025, 4, -38.1235, 144.9779)
    print(f"Temperature: {temp['temperature']} °C")
except NoNearbyPointError as e:
    print(f"No nearby point found: {e}")
```



## Anti-pattern
To use this Python library, you need to download the data first. Please avoid repeatedly downloading the same data, as this service is provided for free and is not intended to handle excessive or redundant downloads. Download the data once and store it locally for reuse.

## Code License
The code in this project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute it for any purpose.

## Data License
This project relies on data from the ERA5 dataset, provided by the European Centre for Medium-Range Weather Forecasts (ECMWF). The ERA5 data is governed by the [Copernicus Licence Agreement](https://apps.ecmwf.int/datasets/licences/copernicus/).

By using this project, you agree to comply with the terms of the Copernicus Licence Agreement when accessing or using ERA5 data.
