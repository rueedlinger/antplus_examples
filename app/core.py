import os
import logging
import logging.config
from pathlib import Path


def setup_logging():
    env_var = "LOGGING_CONF"

    # Check environment variable
    env_path = os.getenv(env_var)
    if env_path and Path(env_path).is_file():
        logging.config.fileConfig(env_path)
        return

    # Check current directory
    current_path = Path.cwd() / "logging.conf"
    if current_path.is_file():
        logging.config.fileConfig(current_path)
        return

    # Check parent directory
    parent_path = Path.cwd().parent / "logging.conf"
    if parent_path.is_file():
        logging.config.fileConfig(parent_path)
        return

    # Fallback
    logging.basicConfig(level=logging.INFO)
