import json
import logging
import subprocess
import sys
import time
from datetime import timedelta

import pandas as pd

from utils.backend_utils import (
    calculate_interval_stats,
    toggle_pump,
    unpack_query_result,
)
from utils.general_utils import (
    fetch_config,
    fetch_src_file_path,
    format_timestamp,
    get_timestamp,
)
from utils.measurering_utils import (
    get_current_humidity,
    get_current_pressure,
    get_current_temperature,
)
from utils.sql_utils import (
    execute_df_to_sql,
    execute_sql_select,
    execute_sql_update,
)
from utils.stat_utils import calculate_dew_point

# Set up logging # TODO consider removing
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a console handler to display logs in the terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter and set it for the handler
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)


def insert_data(db_name, table_name, data) -> None:
    """Inserts data into SQL table."""
    # logger.info(f"*** INSERT INTO {db_name} VALUES {data}") # TODO remove
    execute_sql_update(
        db_name,
        f"INSERT INTO {table_name} VALUES ('{data[0]}', {", ".join(map(str, data[1:]))})",
    )


def main():
    # Fetch config:
    run_config = fetch_config()
    db_cfg = run_config["db"]
    column_names = db_cfg["column_names"]
    logger.info(f"\nLoaded Config:\n{json.dumps(run_config, indent=4)}\n")

    # Create Table
    create_statement = f"""
    CREATE TABLE IF NOT EXISTS {db_cfg["table_name"]} (
        {column_names["timestamp"]} DATETIME,
        {column_names["temperature"]} FLOAT,
        {column_names["mean"]} FLOAT,
        {column_names["median"]} FLOAT,
        {column_names["max"]} FLOAT,
        {column_names["humidity"]} FLOAT,
        {column_names["dew_point"]} FLOAT,
        {column_names["pressure"]} FLOAT
    )
    """

    print(create_statement)
    execute_sql_update(db_cfg["db_name"], create_statement)

    # Allow delay for initialization
    time.sleep(2)

    # Start the Streamlit app
    subprocess.Popen(["streamlit", "run", f"{fetch_src_file_path("frontend.py")}"])

    try:
        while True:
            # Fetch config in case a user changed it:
            run_config = fetch_config()
            db_cfg = run_config["db"]

            # Get fresh readings
            timestamp = get_timestamp()
            temperature = get_current_temperature(run_config)
            pressure = get_current_pressure()
            humidity = get_current_humidity()

            dew_point = calculate_dew_point(db_cfg, temperature, humidity)

            data = {
                column_names["timestamp"]: timestamp,
                column_names["temperature"]: temperature,
                column_names["pressure"]: pressure,
                column_names["humidity"]: humidity,
                column_names["dew_point"]: dew_point,
            }

            # Calculate relevant timeframe:
            analysis_interval = timestamp - timedelta(
                minutes=run_config["analysis_specs"]["interval_minutes"]
            )
            formatted_interval = format_timestamp(analysis_interval)

            # Query all readings for the interval
            interval_temp_query = f"""
            SELECT {column_names["temperature"]}
            FROM {db_cfg["table_name"]}
            WHERE {column_names["timestamp"]} >= '{formatted_interval}'
            """
            interval_temp_query_result = execute_sql_select(
                db_cfg["db_name"], interval_temp_query
            )
            if interval_temp_query_result:
                measurements_list = unpack_query_result(interval_temp_query_result)
            else:
                measurements_list = [data[column_names["temperature"]]]
            data.update(calculate_interval_stats(db_cfg, measurements_list))

            toggle_pump(run_config, data)

            print(f"data = {data}")  # TODO remove

            data_df = pd.DataFrame([data])
            execute_df_to_sql(db_cfg, data_df)
            time.sleep(5)  # get from config
    except Exception as e:
        logger.error(
            f"Error occurred: {e} \n\n\n Traceback: {sys.exception().__traceback__}"
        )
    finally:
        # Cleanup
        pass
        # TODO consider
        # streamlit_process.terminate()


if __name__ == "__main__":
    main()
