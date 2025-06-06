from global_temperature.grids.grid import Grids
import pytest
from scipy.spatial import cKDTree
import numpy as np
from pathlib import Path


# test the singleton pattern
def test_singleton():
    grid1 = Grids()
    grid2 = Grids()
    assert grid1 is grid2, "Grids should be a singleton class"
    assert id(grid1) == id(grid2), "Grids should be a singleton class"


# test loading a grid
def test_load_grid():
    grid = Grids()
    grid.load_grid("src/global_temperature/grids/03x03/data.parquet", "03x03")
    assert "03x03" in grid.grids, "Grid should be loaded"
    assert isinstance(grid.grids["03x03"], cKDTree), "Grid should be a cKDTree"
    assert len(grid.grids["03x03"].data) > 0, "Grid should not be empty"


# test querying a grid of 0.3 x 0.3 degrees
@pytest.mark.parametrize(
    "grid_name,latitude,longitude,expected_point,expected_distance",
    [
        ("03x03", -37.89994, 145.06802, np.array([-37.9, 145.0]), 0.06802),
        ("03x03", 40.7128, -74.0060, np.array([40.7, -74.0]), 0.014136),
        ("03x03", 34.0522, -118.2437, np.array([34.1, -118.1]), 0.15144),
        ("01x01", -37.89994, 145.06802, np.array([-37.9, 145.1]), 0.03198),
        ("01x01", 40.7128, -74.0060, np.array([40.7, -74.0]), 0.014136),
        ("01x01", 34.0522, -118.2437, np.array([34.1, -118.2]), 0.064765),
    ],
)
def test_query_grid(grid_name, latitude, longitude, expected_point, expected_distance):
    grid = Grids()
    grid.load_grid(
        Path(__file__).parents[1]
        / f"src/global_temperature/grids/{grid_name}/data.parquet",
        grid_name,
    )

    point, distance = grid.query(grid_name, latitude, longitude)
    assert isinstance(point, np.ndarray), "Query should return a tuple"
    assert len(point) == 2, "Query should return a tuple of length 2"
    assert isinstance(distance, np.float32), "Distance should be a np.float32"
    assert np.allclose(point, expected_point), "Query should return the correct point"
    assert (
        pytest.approx(distance, rel=1e-3) == expected_distance
    ), "Distance should be correct"


def test_query_invalid_grid():
    grid = Grids()
    with pytest.raises(ValueError):
        # "02x02" is an invalid grid name
        grid.query("02x02", -37.89994, 145.06802)
