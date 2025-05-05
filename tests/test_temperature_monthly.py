from global_temperature.temperature_monthly import TemperatureMonthly
import pytest
import numpy as np


@pytest.fixture
def monthly_instance_1():
    """Fixture to set up the TemperatureMonthly instance using 0.3 x 0.3 degrees (not in used)."""
    temp_monthly = TemperatureMonthly(
        search_radius=0.3,
        geohash_precision=2,
        max_cache_size=100,
        grid_name="03x03",
    )
    return temp_monthly


@pytest.mark.parametrize(
    "year, month, latitude, longitude, expected_temperature",
    [
        # Melbourne
        (2025, 1, -37.89994, 145.06802, 20.79),
        # New York
        (2020, 1, 40.7128, -74.0060, 2.75),
        # Los Angeles
        (2010, 1, 34.0522, -118.2437, 11.27),
        (2010, 3, 34.0522, -118.2437, 13.14),
        (2010, 6, 34.0522, -118.2437, 19.63),
        (2010, 9, 34.0522, -118.2437, 22.65),
        (2010, 12, 34.0522, -118.2437, 11.52),
    ],
)
def test_TemperatureMonthly_1(
    monthly_instance_1, year, month, latitude, longitude, expected_temperature
):
    """test TemperatureMonthly instance"""
    assert isinstance(
        monthly_instance_1, TemperatureMonthly
    ), "Should be an instance of TemperatureMonthly"

    # test query method
    temperature = monthly_instance_1.query(
        year=year,
        month=month,
        latitude=latitude,
        longitude=longitude,
    )

    assert np.isclose(
        temperature, expected_temperature, rtol=1e-2
    ), f"Expected temperature: {expected_temperature}, but got: {temperature}"


@pytest.fixture
def monthly_instance_2():
    """Fixture to set up the TemperatureMonthly instance using 0.1 x 0.1 degrees."""
    temp_monthly = TemperatureMonthly(
        search_radius=0.1,
        geohash_precision=1,
        max_cache_size=100,
        grid_name="01x01",
    )
    return temp_monthly


@pytest.mark.parametrize(
    "year, month, latitude, longitude, expected_temperature",
    [
        # Melbourne
        (2024, 1, -37.89994, 145.06802, 19.69),
        # New York
        (2024, 1, 40.7128, -74.0060, 1.18),
        # # Los Angeles
        (2011, 1, 34.0522, -118.2437, 11.59),
        (2011, 3, 34.0522, -118.2437, 12.88),
        (2011, 6, 34.0522, -118.2437, 19.01),
        (2011, 9, 34.0522, -118.2437, 22.57),
        (2011, 12, 34.0522, -118.2437, 10.34),
    ],
)
def test_TemperatureMonthly_2(
    monthly_instance_2, year, month, latitude, longitude, expected_temperature
):
    """test TemperatureMonthly instance"""
    assert isinstance(
        monthly_instance_2, TemperatureMonthly
    ), "Should be an instance of TemperatureMonthly"

    # test query method
    temperature = monthly_instance_2.query(
        year=year,
        month=month,
        latitude=latitude,
        longitude=longitude,
    )

    assert np.isclose(
        temperature, expected_temperature, rtol=1e-2
    ), f"Expected temperature: {expected_temperature}, but got: {temperature}"
