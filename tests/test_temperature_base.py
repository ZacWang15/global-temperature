from global_temperature.temperature_base import TemperatureBase
import numpy as np
import pytest


def test_TemperatureBase():
    """
    Test the TemperatureBase class.
    """

    # Create a mock subclass of TemperatureBase
    class MockTemperature(TemperatureBase):
        def query(self, *args, **kwargs):
            return 1.0

    # Create an instance of the mock subclass
    temp = MockTemperature()

    # Test the query method
    result = temp.query()
    assert result == 1.0, "Query method should return 1.0"

    # Test snap()
    point, distance = temp.snap(-37.89994, 145.06802)

    assert np.array_equal(
        point, np.array([-37.9, 145.0])
    ), "Query should return the correct point"
    assert (
        pytest.approx(distance, rel=1e-3) == 0.06802
    ), "Distance should be correct"
