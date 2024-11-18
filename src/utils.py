import json
import os

import yaml


def fetch_config() -> dict: #TODO change to class?
    # Get the current directory of the script
    current_dir = os.path.dirname(__file__)

    # Load Config
    # Define the path to the YAML file
    config_file_path = os.path.join(current_dir, "..", "config", "config.yaml")
    # Load the YAML file
    with open(config_file_path) as file:
        config = yaml.safe_load(file)
    print(f"\nLoaded Config:\n{json.dumps(config, indent=4)}\n")
    return config