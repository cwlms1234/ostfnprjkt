import os

import yaml

### Config

def fetch_config_file_path(filename: str) -> str:
    # Define the path to the YAML file
    return os.path.join(os.path.join( os.path.dirname( __file__ ), '..' ), "config", filename)


def fetch_config(name: str = "config.yaml") -> dict:  # TODO change to class? TODO Doscstring
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


### SQL

