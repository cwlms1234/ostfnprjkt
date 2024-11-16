import os
import time

import yaml

from fan_tool.measuring_assets.test_prop import fetch_temperature_measuring_test
from fan_tool.measuring_assets.utils.measuring_utils import get_timestamp, write_to_file

# Get the current directory of the script
current_dir = os.path.dirname(__file__)

# Load Config
# Define the path to the YAML file
config_file_path = os.path.join(current_dir, "..", "config", "config.yaml")
# Load the YAML file
with open(config_file_path) as file:
    config = yaml.safe_load(file)
print(f"Loaded Config: {config}")

temp_measure = 25 # TODO remove after testing

while True:
    temp_measure = fetch_temperature_measuring_test(temp_measure, config["test_values"])
    timestamp = get_timestamp()
    print(
        f"Measured {temp_measure} degrees Celsius at {timestamp}"
    )
    data = (timestamp, temp_measure)


    write_to_file(config["execution_specs"], data)





    time.sleep(5)
    #time.sleep(config["execution_specs"].update_interval)