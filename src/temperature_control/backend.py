import json
import subprocess
import time
import traceback
from datetime import timedelta

import pandas as pd
from gpiozero import OutputDevice

from temperature_control.utils.backend_utils import (
    calculate_interval_stats,
    get_console_logger,
    toggle_pump,
    unpack_query_result,
)
from temperature_control.utils.general_utils import (
    fetch_config,
    fetch_src_file_path,
    format_timestamp,
    get_timestamp,
)
from temperature_control.utils.measurering_utils import (
    get_current_humidity,
    get_current_pressure,
    get_current_temperature,
)
from temperature_control.utils.sql_utils import (
    execute_df_to_sql,
    execute_sql_select,
    execute_sql_update,
    table_maintenance,
)
from temperature_control.utils.stat_utils import calculate_dew_point

# Set up logging:


def main():
    # Fetch config:
    run_config = fetch_config()
    logger = get_console_logger()
    output_device_list = []
    db_cfg = run_config["db"]
    column_names = db_cfg["column_names"]
    logger.info(f"\nLoaded Config:\n{json.dumps(run_config, indent=4)}\n")
    pump_status = False
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

    # Initialize Output devices:
    if run_config["execution_specs"].get("gpio_pin_1"):
        output_1 = OutputDevice(
            pin=run_config["execution_specs"].get("gpio_pin_1"),
            active_high=False,
            initial_value=False,
        )
        output_device_list.append(output_1)

    else:
        output_1 = None

    if run_config["execution_specs"].get("gpio_pin_2"):
        output_2 = OutputDevice(
            pin=run_config["execution_specs"].get("gpio_pin_2"),
            active_high=False,
            initial_value=False,
        )
        output_device_list.append(output_2)

    else:
        output_2 = None

    logger.info(f"Initialized output devices {output_device_list}")

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
            pressure = get_current_pressure(run_config)
            humidity = get_current_humidity(run_config)

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
            pump_status = toggle_pump(
                cfg=run_config,
                data=data,
                previous_run=pump_status,
            )
            # Pump_status
            if pump_status:
                for device in output_device_list:
                    device.on()
            else:
                for device in output_device_list:
                    device.off()

            data.update(
                {
                    column_names["pump_activation"]: run_config["execution_specs"][
                        "update_frequency"
                    ]
                }
            )

            data_df = pd.DataFrame([data])
            execute_df_to_sql(db_cfg, data_df)
            time.sleep(run_config["execution_specs"]["update_frequency"])
    except Exception as e:
        logger.error(
            f"Error occurred in backend.py: {e} \nTraceback: {traceback.format_exc()}"
        )
    finally:
        if output_1:
            output_1.off()
        if output_2:
            output_2.off()


if __name__ == "__main__":
    main()
