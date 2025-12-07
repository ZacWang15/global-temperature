# Global Temperature

[![PyPI version](https://badge.fury.io/py/global-temperature.svg)](https://badge.fury.io/py/global-temperature)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project provides average monthly temperature (Celsius) globally for land areas using 0.1° × 0.1° grids.

The data spans from 1970-01 to 2025-11 with monthly intervals, and the dataset is updated monthly for the current year.

The tool can match any latitude/longitude point to the nearest grid point and return the temperature for a specified year and month.

## Coverage
The yellow areas in this [coverage map](https://global-temperature.com/coverage.png) show the geographical coverage of the project.

## Data Architecture

The temperature data is partitioned by year, month, and geohash, resulting in small, focused data files ranging from 10KB to 500KB each. This efficient partitioning strategy offers several advantages:

- **API-Friendly**: Small file sizes make the data suitable for serving behind APIs
- **Fast Loading**: Only relevant data partitions are loaded on-demand
- **Memory Efficient**: Reduced memory footprint with targeted data access
- **Scalable**: Easy to cache and distribute individual partitions

## Quick Start

### Installation
Requires Python >= 3.10
```bash
pip install global-temperature
```

### Basic Usage
```python
from global_temperature.tools.download import download
import global_temperature as gt

# 1. Download data (do this once)
download(years=[2024], target_path="data")

# 2. Create temperature object
temp_tool = gt.TemperatureFactory.create_temperature_object(
    data_type="monthly",
    source_folder="data"
)

# 3. Query temperature
result = temp_tool.query(2024, 6, 40.7128, -74.0060)  # NYC
print(f"Temperature: {result['temperature']:.1f}°C")
```

## Detailed Usage

### 1. Download Temperature Data

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

### 2. Query Temperature Data

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

### 3. Understanding the Response

The query method returns a dictionary with detailed information:

```python
print(temp)
# Output:
# {
#     'temperature': np.float32(17.178528),      # Temperature in Celsius
#     'geohash': 'r',                            # Geohash of nearest grid point (data is partitioned by year/month/geohash)
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

## API Reference

### TemperatureFactory.create_temperature_object()

**Parameters:**
- **data_type** (`str`): Currently supports "monthly" for monthly temperature data
- **source_folder** (`str`): Directory containing the downloaded temperature data files
- **search_radius** (`float`, optional): Maximum distance (in degrees) to search for the nearest grid point. Default: 0.1
- **max_cache_size** (`int`, optional): Maximum number of data partitions to keep in memory cache. Each partition represents one year/month/geohash combination. Default: 200

### query(year, month, latitude, longitude)

**Parameters:**
- **year** (`int`): Year (1970-2025)
- **month** (`int`): Month (1-12)
- **latitude** (`float`): Latitude in decimal degrees
- **longitude** (`float`): Longitude in decimal degrees

**Returns:** Dictionary with temperature data and metadata

## Performance Tips

- **Create the temperature object once** and reuse it for multiple queries
- **Increase max_cache_size** if you're querying many different locations/times and have sufficient memory
- **Use absolute paths** for better reliability when specifying data directories
- **Download data once** and store locally to avoid repeated API calls

## Examples

You can find additional usage examples in the [`examples.py`](examples.py) file.

## Important Usage Guidelines

⚠️ **Anti-pattern**: To use this Python library, you need to download the data first. Please avoid repeatedly downloading the same data, as this service is provided for free and is not intended to handle excessive or redundant downloads. Download the data once and store it locally for reuse.

## Data Source

This project uses temperature data from the ERA5 reanalysis dataset, which provides high-quality atmospheric data based on weather observations and numerical weather prediction models.

## License

### Code License
The code in this project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute it for any purpose.

### Data License
This project relies on data from the ERA5 dataset, provided by the European Centre for Medium-Range Weather Forecasts (ECMWF). The ERA5 data is governed by the [Copernicus License Agreement](https://apps.ecmwf.int/datasets/licences/copernicus/).

By using this project, you agree to comply with the terms of the Copernicus License Agreement when accessing or using ERA5 data.

## Contributing

Issues and pull requests are welcome! Please feel free to contribute to this project.

## Support

If you encounter any problems or have questions, please [open an issue](https://github.com/ZacWang15/global-temperature/issues) on GitHub.