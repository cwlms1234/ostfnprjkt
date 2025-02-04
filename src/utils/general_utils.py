import os
from datetime import datetime

import pytz
import yaml

### Config


def fetch_config_file_path(filename: str) -> str:
    # Define the path to the YAML file
    return os.path.join(
        os.path.join(os.path.dirname(__file__), ".."), "config", filename
    )


def fetch_src_file_path(filename: str) -> str:
    return os.path.join(os.path.join(os.path.dirname(__file__), ".."), filename)


def fetch_config(
    name: str = "config.yaml",
) -> dict:  # TODO change to class? TODO Doscstring
    # # Get the current directory of the script
    # current_dir = os.path.dirname(__file__)

    # # Load Config
    # # Define the path to the YAML file
    # config_file_path = os.path.join(current_dir, "config", "config.yaml")
    # # Load the YAML file # TODO delete after testing

    config_file_path = fetch_config_file_path(name)

    with open(config_file_path) as file:
        config = yaml.safe_load(file)
    return config


def write_config(cfg: dict) -> None:
    """Write changed config to file"""

    config_file_path = fetch_config_file_path("config.yaml")
    with open(config_file_path, "w") as file:
        yaml.dump(cfg, file)


### Time
def get_timestamp() -> datetime:
    """Get the current time in the Berlin time zone"""
    berlin_tz = pytz.timezone("Europe/Berlin")
    timestamp = datetime.now(berlin_tz)
    return format_timestamp(timestamp)


def format_timestamp(timestamp: datetime) -> datetime:
    """Return the current time in the Berlin time zone"""
    return timestamp.replace(
        hour=timestamp.hour,
        minute=timestamp.minute,
        second=timestamp.second,
        microsecond=0,
    )


def get_date():
    """Get the current year and month"""
    berlin_tz = pytz.timezone("Europe/Berlin")
    return datetime.now(berlin_tz).strftime("%m-%Y")
