import json
import logging
import subprocess
import time
import traceback
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
    table_maintenance,
)
from utils.stat_utils import calculate_dew_point

# Set up logging:
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


def main():
    # Fetch config:
    run_config = fetch_config()
    db_cfg = run_config["db"]
    column_names = db_cfg["column_names"]
    logger.info(f"\nLoaded Config:\n{json.dumps(run_config, indent=4)}\n")
    pump_status = None

    # Create Table
    create_statement = f"""
    CREATE TABLE IF NOT EXISTS {db_cfg["table_name"]} (
        '{column_names["timestamp"]}' DATETIME,
        '{column_names["temperature"]}' FLOAT,
        '{column_names["mean"]}' FLOAT,
        '{column_names["median"]}' FLOAT,
        '{column_names["max"]}' FLOAT,
        '{column_names["humidity"]}' FLOAT,
        '{column_names["dew_point"]}' FLOAT,
        '{column_names["pressure"]}' FLOAT,
        '{column_names["weekday"]}' STRING,
        '{column_names["hour_interval"]}' INTEGER,
        '{column_names["pump_activation"]}' INTEGER,
        '{column_names["update_interval"]}' INTEGER
    )
    """

    execute_sql_update(db_cfg["db_name"], create_statement, logger)
    logger.info(f"Executed: {create_statement}")

    # This will delete all data that's older than the config's "retention_days" value
    table_maintenance(db_cfg)

    # Allow delay for initialization before starting frontend
    time.sleep(2)

    # Start the Streamlit app
    subprocess.Popen(["streamlit", "run", f"{fetch_src_file_path('frontend.py')}"])

    try:
        while True:
            # Fetch config in case a user changed it between iterations:
            run_config = fetch_config()
            db_cfg = run_config["db"]

            # Get fresh readings
            timestamp = get_timestamp()
            temperature = get_current_temperature(run_config)
            pressure = get_current_pressure()
            humidity = get_current_humidity()

            dew_point = calculate_dew_point(db_cfg, temperature, humidity)

            # Put data into dictionary structure for later insert into DB
            data = {
                column_names["timestamp"]: timestamp,
                column_names["temperature"]: temperature,
                column_names["pressure"]: pressure,
                column_names["humidity"]: humidity,
                column_names["dew_point"]: dew_point,
                column_names["update_interval"]: run_config["execution_specs"][
                    "update_frequency"
                ],
            }

            # Calculate relevant timeframe for statistical metrics:
            analysis_interval = timestamp - timedelta(
                minutes=run_config["analysis_specs"]["interval_minutes"]
            )
            formatted_interval = format_timestamp(analysis_interval)

            # Query all data points for the timeframe
            interval_temp_query = f"""
            SELECT {column_names["temperature"]}
            FROM {db_cfg["table_name"]}
            WHERE {column_names["timestamp"]} >= '{formatted_interval}'
            """

            interval_temp_query_result = execute_sql_select(
                db_cfg["db_name"], interval_temp_query
            )
            current_temp = data[column_names["temperature"]]
            if interval_temp_query_result:
                measurements_list = unpack_query_result(interval_temp_query_result)
                # The current temp has not yet been added to the DB
                measurements_list.append(current_temp)
            else:
                # If there are no previous datapoints, the current temp is the only one
                measurements_list = [current_temp]
            data.update(calculate_interval_stats(db_cfg, measurements_list))

            # Check whether the pump has to be activated
            pump_status = toggle_pump(run_config, data, pump_status)
            data.update(pump_status)

            data_df = pd.DataFrame([data])
            execute_df_to_sql(db_cfg, data_df)
            time.sleep(run_config["execution_specs"]["update_frequency"])
    except Exception as e:
        logger.error(
            f"Error occurred in backend.py: {e} \nTraceback: {traceback.format_exc()}"
        )
    finally:
        # Cleanup
        pass


if __name__ == "__main__":
    main()
