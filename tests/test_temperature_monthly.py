from global_temperature.temperature_monthly import TemperatureMonthly
import pytest
import numpy as np


@pytest.fixture
def monthly_instance():
    """Fixture to set up the TemperatureMonthly instance."""
    temp_monthly = TemperatureMonthly(
        max_cache_size=100,
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
def test_TemperatureMonthly(
    monthly_instance, year, month, latitude, longitude, expected_temperature
):
    """test TemperatureMonthly instance"""
    assert isinstance(
        monthly_instance, TemperatureMonthly
    ), "Should be an instance of TemperatureMonthly"

    # test query method
    temperature = monthly_instance.query(
        year=year,
        month=month,
        latitude=latitude,
        longitude=longitude,
    )

    assert np.isclose(
        temperature, expected_temperature, rtol=1e-2
    ), f"Expected temperature: {expected_temperature}, but got: {temperature}"
