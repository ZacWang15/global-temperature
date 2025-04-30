from global_temperature.config import load_config


def test_load_config():
    """Test loading the configuration file."""
    config = load_config()
    assert isinstance(config, dict), "Config should be a dictionary"
    assert "grids" in config, "Config should contain 'grids' key"
