import random
import sqlite3
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from temperature_control.utils.general_utils import fetch_config, get_timestamp


def generate_synthetic_data():
    cfg = fetch_config()
    db_cfg = cfg["db"]
    col_names = cfg["db"]["column_names"]
    round_decimal = db_cfg["round_decimal"]
    update_frequency = cfg["execution_specs"]["update_frequency"]

    num_days = 365

    timestamps = []
    dew_point = []
    humidity = []
    max_temp = []
    mean_temp = []
    median_temp = []
    pressure = []
    temperature = []
    hour_interval = []
    pump_activation = []
    update_interval = []

    start_date = get_timestamp() - timedelta(days=365) # Starting date
    current_time = start_date  # Set current_time to the start date

    # Simulate the data for each update interval (every `update_frequency` seconds)
    total_seconds = num_days * 24 * 60 * 60  # Total seconds in the year
    for t in range(
        0, total_seconds, update_frequency
    ):  # Update in intervals of `update_frequency`
        # Generate data for the current time
        timestamps.append(current_time.strftime("%Y-%m-%d %H:%M:%S"))
        dew_point.append(round(np.random.uniform(0, 20), round_decimal))
        humidity.append(round(np.random.uniform(30, 90), round_decimal))
        max_temp.append(round(np.random.uniform(15, 35), round_decimal))
        mean_temp.append(round(np.random.uniform(15, 30), round_decimal))
        median_temp.append(round(np.random.uniform(15, 30), round_decimal))
        pressure.append(round(np.random.uniform(1000, 1030), round_decimal))
        temperature.append(round(np.random.uniform(15, 35), round_decimal))
        pump_activation.append(random.choice([0, cfg["execution_specs"]["update_frequency"]]))
        update_interval.append(cfg["execution_specs"]["update_frequency"])

        # Increment the current time by `update_frequency` seconds
        current_time += timedelta(seconds=update_frequency)

    # Create a DataFrame with the generated data
    data = pd.DataFrame(
        {
            col_names["timestamp"]: timestamps,
            col_names["temperature"]: temperature,
            col_names["dew_point"]: dew_point,
            col_names["humidity"]: humidity,
            col_names["max"]: max_temp,
            col_names["mean"]: mean_temp,
            col_names["median"]: median_temp,
            col_names["pressure"]: pressure,
            col_names["pump_activation"]: pump_activation,
            col_names["update_interval"]: update_interval,
        }
    )

    # Create and connect to the database
    conn = sqlite3.connect(db_cfg["db_name"])
    cursor = conn.cursor()

    # Create the table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {db_cfg["table_name"]} (
        {col_names["temperature"]} REAL,
        {col_names["timestamp"]} TEXT,
        {col_names["dew_point"]} REAL,
        {col_names["humidity"]} REAL,
        {col_names["max"]} REAL,
        {col_names["mean"]} REAL,
        {col_names["median"]} REAL,
        {col_names["pressure"]} REAL,
        {col_names["pump_activation"]} INT,
        {col_names["update_interval"]} INT
    );
    """)

    print(
        f"Generated data for {len(timestamps)} updates, with an update frequency of {update_frequency} seconds."
    )

    # Insert data into the table
    for _, row in data.iterrows():
        insert_stmnt = f"""
        INSERT INTO {db_cfg["table_name"]} (
                    {col_names["timestamp"]}, {col_names["temperature"]}, {col_names["dew_point"]}, {col_names["humidity"]}, {col_names["max"]}, {col_names["mean"]}, {col_names["median"]}, {col_names["pressure"]}, {col_names["pump_activation"]}, {col_names["update_interval"]} 
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(insert_stmnt, tuple(row))

    # Commit and close
    conn.commit()
    conn.close()


def main():
    generate_synthetic_data()


if __name__ == "__main__":
    main()
