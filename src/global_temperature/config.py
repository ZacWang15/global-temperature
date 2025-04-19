from pathlib import Path
import yaml

# Resolve paths relative to the package root
PACKAGE_ROOT = Path(__file__).parent
CONFIG_FILE = PACKAGE_ROOT / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_FILE, "r") as file:
        return yaml.safe_load(file)
