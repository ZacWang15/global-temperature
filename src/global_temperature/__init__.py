import logging
from datetime import datetime
from pathlib import Path

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
    logger.setLevel(logging.INFO)
    # Prevent the logger from propagating to the root logger
    logger.propagate = False
