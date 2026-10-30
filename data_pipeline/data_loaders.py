# data_loaders.py
from pathlib import Path

import logging
import pandas as pd
import json
import yaml


# Do not call logging.basicConfig() here.
# Use the logging configuration from Part 1.
logger = logging.getLogger(__name__)


def load_csv(filepath):
    """Load a CSV file into a DataFrame."""
    data = pd.read_csv(filepath)
    logger.info("Loaded CSV file: %s (%d rows)", filepath, len(data))
    return data


def load_json(filepath):
    """Load a JSON file into a Python object (dict or list)."""
    with open(filepath) as file:
        data = json.load(file)

    logger.info("Loaded JSON file: %s", filepath)
    return data


def load_yaml(filepath):
    """Load a YAML file into a Python object."""
    with open(filepath) as file:
        data = yaml.safe_load(file)

    logger.info("Loaded YAML file: %s", filepath)
    return data


def load_data(filepath):
    """Load a file based on its extension."""
    path = Path(filepath)
    extension = path.suffix.lower()

    if extension == ".csv":
        return load_csv(path)

    if extension == ".json":
        return load_json(path)

    if extension == ".yaml":
        return load_yaml(path)

    logger.error("Unsupported file format: %s", extension)
    raise ValueError(f"Unsupported file format: {extension}")