import json
import os
import sqlite3

import pandas as pd
import yaml


def fetch_config_file_path(filename: str) -> str:
    # Get the current directory of the script
    current_dir = os.path.dirname(__file__)

    # Define the path to the YAML file
    return os.path.join(current_dir, "config", filename)


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
    print(f"\nLoaded Config:\n{json.dumps(config, indent=4)}\n")
    return config


def write_config(cfg: dict) -> None:
    """Write changed config to file"""

    config_file_path = fetch_config_file_path("config.yaml")
    with open(config_file_path, "w") as file:
        yaml.dump(cfg, file)


def execute_sql_update(db_name: str, statement: str):
    try:
        with sqlite3.connect(db_name) as conn:
            conn.execute(statement)
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)


def execute_sql_select(db_name: str, statement: str, unpack_first_value: bool = False) -> list:
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(statement)
            result = cursor.fetchall()
            if unpack_first_value == True:
                result = result[0][0]
        return result
    except sqlite3.Error as e:
        print(e)


def execute_sql_to_df(db_name: str, statement: str) -> pd.DataFrame:
    try:
        with sqlite3.connect(db_name) as conn:
            df = pd.read_sql_query(statement, conn)
        return df
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)
