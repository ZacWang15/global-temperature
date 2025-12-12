import logging
from datetime import datetime
from pathlib import Path
import time
from .config import load_config
from .temperature import TemperatureFactory
from .temperature_base import TemperatureQueryResult


# Load the configuration
CONFIG = load_config()

# Package-level logger
logger = logging.getLogger(__name__)

# Default configuration (only if no handlers exist yet)
if not logger.handlers:
    # Create a 'log' folder in the same directory
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True, parents=True)

    # Generate a log file name with a timestamp
    log_file = log_dir / f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    # Specify log file path
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Output to console
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Set the logging level
    logger.setLevel(CONFIG["logging"]["level"])
    # Prevent the logger from propagating to the root logger
    logger.propagate = False


def delete_old_logs(log_dir: Path, days: int = 7):
    """
    Delete log files older than a specified number of days.

    Args:
        log_dir (Path): Path to the logs directory.
        days (int): Number of days to keep log files. Files older than this will be deleted.
    """
    # Get the current time
    now = time.time()

    # Iterate through all files in the log directory
    for log_file in log_dir.glob("*.log"):
        # Get the file's last modification time
        file_age = now - log_file.stat().st_mtime

        # Convert days to seconds and check if the file is older
        if file_age > days * 86400:  # 86400 seconds in a day
            try:
                log_file.unlink()  # Delete the file
                print(f"Deleted old log file: {log_file}")
            except Exception as e:
                print(f"Error deleting file {log_file}: {e}")


log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True, parents=True)


# Delete logs older than rention_period
delete_old_logs(log_dir, days=CONFIG["logging"]["rention_period"])
