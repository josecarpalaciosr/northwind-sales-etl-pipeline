"""Configure logging for the Northwind ETL application."""

import logging
from pathlib import Path


# Locate the project root independently of where the repository is cloned.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Define the directory and file used to preserve pipeline execution logs.
LOG_DIRECTORY = PROJECT_ROOT / "logs"
LOG_FILE_PATH = LOG_DIRECTORY / "pipeline.log"

# Define a consistent structure for every generated log record.
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging() -> None:
    """Configure console and file logging for the ETL application."""

    # Create the log directory if it is unavailable in the local environment.
    LOG_DIRECTORY.mkdir(parents=True, exist_ok=True)

    # Configure the root logger once for every module in the application.
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                LOG_FILE_PATH,
                mode="a",
                encoding="utf-8",
            ),
        ],
    )