import json
import logging
import subprocess
import sys
import time
from datetime import timedelta

import pandas as pd

from measuring_assets.measuring import (
    measure_temp,
)
from measuring_assets.utils.measuring_utils import format_timestamp, get_timestamp
from utils.backend_utils import (
    calculate_interval_stats,
    toggle_pump,
    unpack_query_result,
)
from utils.general_utils import fetch_config
from utils.measurering_utils import get_current_humidity, get_current_pressure
from utils.sql_utils import (
    execute_df_to_sql,
    execute_sql_select,
    execute_sql_update,
)

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
    db_cfg = run_config["sqlite"]
    logger.info(f"\nLoaded Config:\n{json.dumps(run_config, indent=4)}\n")

    # Create Table
    create_statement = f"""
    CREATE TABLE IF NOT EXISTS {db_cfg["table_name"]} (
        {db_cfg["column_names"]["timestamp"]} DATETIME,
        {db_cfg["column_names"]["reading"]} FLOAT,
        {db_cfg["column_names"]["mean"]} FLOAT,
        {db_cfg["column_names"]["median"]} FLOAT,
        {db_cfg["column_names"]["max"]} FLOAT,
        {db_cfg["column_names"]["humidity"]} FLOAT,
        {db_cfg["column_names"]["dew_point"]} FLOAT,
        {db_cfg["column_names"]["pressure"]} FLOAT
    )
    """

    print(create_statement)
    execute_sql_update(db_cfg["db_name"], create_statement)

    # Allow delay for initialization
    time.sleep(2)

    # Start the Streamlit app
    subprocess.Popen(["streamlit", "run", "src/frontend.py"])

    try:
        while True:
            # Fetch config in case a user changed it:
            run_config = fetch_config()
            db_cfg = run_config["sqlite"]

            data = measure_temp(run_config)

            # Calculate relevant timeframe:
            analysis_interval = get_timestamp() - timedelta(
                minutes=run_config["analysis_specs"]["interval_minutes"]
            )
            formatted_interval = format_timestamp(analysis_interval)

            # Query all readings for the interval
            interval_temp_query = f"""
            SELECT {db_cfg["column_names"]["reading"]}
            FROM {db_cfg["table_name"]}
            WHERE {db_cfg["column_names"]["timestamp"]} >= '{formatted_interval}'
            """
            interval_temp_query_result = execute_sql_select(
                db_cfg["db_name"], interval_temp_query
            )
            if interval_temp_query_result:
                measurements_list = unpack_query_result(interval_temp_query_result)
            else:
                measurements_list = [data[db_cfg["column_names"]["reading"]]]
            data.update(calculate_interval_stats(run_config, measurements_list))

            pressure = get_current_pressure()
            humidity = get_current_humidity()

            
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
