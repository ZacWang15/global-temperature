from global_temperature.temperature_base import TemperatureBase


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

    # test snap()
    print(temp.snap(-37.89994, 145.06802))
