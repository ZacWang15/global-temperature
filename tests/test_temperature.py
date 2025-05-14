import global_temperature as gt
from global_temperature.temperature_monthly import TemperatureMonthly
import pytest


def test_temperature():
    temperature = gt.TemperatureFactory.create_temperature_object(
        data_type="monthly",
        source_folder="examples/data",
    )
    assert isinstance(temperature, TemperatureMonthly)
    assert temperature.source_folder == "examples/data"


def test_temperature_fail():
    with pytest.raises(ValueError):
        temperature = gt.TemperatureFactory.create_temperature_object(
            data_type="daily",
            source_folder="examples/data",
        )
