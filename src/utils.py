import json
import os
import sqlite3

import pandas as pd
import yaml


def fetch_config() -> dict:  # TODO change to class?
    # Get the current directory of the script
    current_dir = os.path.dirname(__file__)

    # Load Config
    # Define the path to the YAML file
    config_file_path = os.path.join(current_dir, "config", "config.yaml")
    # Load the YAML file
    with open(config_file_path) as file:
        config = yaml.safe_load(file)
    print(f"\nLoaded Config:\n{json.dumps(config, indent=4)}\n")
    return config

def execute_sql_update(db_name: str, statement: str):
    try:
        with sqlite3.connect(db_name) as conn:
            conn.execute(statement)
    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)

def execute_sql_select(db_name:str, statement:str) -> list:
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(statement)
            result = cursor.fetchall()
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
