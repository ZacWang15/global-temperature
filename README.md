# Global Temperature

This project provides average monthly temperature (celsius degree) globally in land area by 0.1 degree x 0.1 degree grids.

The data is at monthly interval from 1990 till now and dataset will update every month for the current year.

The tool can match a latitude, longitude point to the nearest point in the grid and return the celsius degree according to year, month you pass to it.

## Converage
The yellow area in the [photo](https://global-temperature.com/coverage.png) is the coverage of the project.


## Install
Require Python >= 3.10
> pip install global-temperature

## How to use

You can find usage examples in the [`examples.py`](examples.py) file.

[View the examples.py file](https://github.com/ZacWang15/global-temperature/blob/master/examples.py)


## Anti-pattern
To use this Python library, you need to download the data first. Please avoid repeatedly downloading the same data, as this service is provided for free and is not intended to handle excessive or redundant downloads. Download the data once and store it locally for reuse.

## Code License
The code in this project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute it for any purpose.

## Data License
This project relies on data from the ERA5 dataset, provided by the European Centre for Medium-Range Weather Forecasts (ECMWF). The ERA5 data is governed by the [Copernicus Licence Agreement](https://apps.ecmwf.int/datasets/licences/copernicus/).

By using this project, you agree to comply with the terms of the Copernicus Licence Agreement when accessing or using ERA5 data.