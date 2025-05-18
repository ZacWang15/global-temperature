import global_temperature.tools.validate as vd
from global_temperature.errors import NoNearbyPointError
import pytest


def test_check_within_radius():
    """
    Test the check_within_radius function.
    """
    assert vd.check_within_radius(0.3, 0.2) is True
    assert vd.check_within_radius(0.3, 0.3) is True

    with pytest.raises(NoNearbyPointError):
        vd.check_within_radius(0.3, 0.4)

    with pytest.raises(ValueError):
        vd.check_within_radius(-0.1, 0.2)


def test_check_year():
    """
    Test the check_year function.
    """
    assert vd.check_year(2023) is True
    assert vd.check_year(1970) is True

    with pytest.raises(ValueError):
        vd.check_year(1989)

    with pytest.raises(ValueError):
        vd.check_year(2026)

    with pytest.raises(ValueError):
        vd.check_year("2023")
