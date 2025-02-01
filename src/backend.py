import json
import logging
import statistics
import subprocess
import time
from datetime import timedelta

from measuring_assets.measuring import (
    measure_temp,
)
from measuring_assets.utils.measuring_utils import format_timestamp, get_timestamp
from utils import execute_sql_select, execute_sql_update, fetch_config

# Set up logging # TODO consider removing
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a console handler to display logs in the terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a formatter and set it for the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)
       


def collect_data(run_config: dict) -> dict:
    """Collects temperature data."""
    return measure_temp(run_config)

def insert_data(db_name, table_name, data) -> None:
    """Inserts data into SQL table."""
    #logger.info(f"*** INSERT INTO {db_name} VALUES {data}") # TODO remove
    execute_sql_update(db_name, f"INSERT INTO {table_name} VALUES ('{data[0]}', {", ".join(map(str, data[1:]))})")

    
def main():

    # Fetch config:
    run_config = fetch_config()
    db_cfg = run_config["sqlite"]
    logger.info(f"\nLoaded Config:\n{json.dumps(run_config, indent=4)}\n")

    
    #Create Table
    create_statement = f"""
    CREATE TABLE IF NOT EXISTS {db_cfg["table_name"]} (
        {db_cfg["column_names"]["timestamp"]} DATETIME,
        {db_cfg["column_names"]["reading"]} FLOAT,
        {db_cfg["column_names"]["mean"]} FLOAT,
        {db_cfg["column_names"]["median"]} FLOAT,
        {db_cfg["column_names"]["max"]} FLOAT
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
            
            data = collect_data(run_config)
            # Calculate relevant timeframe:
            analysis_interval = get_timestamp() - timedelta(minutes=run_config["analysis_specs"]["interval_minutes"])
            formatted_interval = format_timestamp(analysis_interval)
            
            # Query all readings for the interval
            interval_temp_query = f"""
            SELECT {db_cfg["column_names"]["reading"]}
            FROM {db_cfg["table_name"]}
            WHERE {db_cfg["column_names"]["timestamp"]} >= '{formatted_interval}'
            """
            interval_temps = execute_sql_select(db_cfg["db_name"], interval_temp_query)
            
            # Statistics need at least one data point
            if interval_temps:
                # Convert list of 1 element tuples into flat list:
                interval_temps = [row[0] for row in interval_temps]
                print(f"interval_temps = {interval_temps}") # TODO remove
                mean_temp = statistics.mean(interval_temps)
                mean_temp = round(mean_temp, 1)
                median_temp = statistics.median(interval_temps)
                max_temp = max(interval_temps)
                data += (mean_temp, median_temp, max_temp)
            else:
                data += (data[1], data[1], data[1])

            print(f"data = {data}") #TODO remove

            insert_data(db_cfg["db_name"], db_cfg["table_name"], data)
            time.sleep(5) # get from config
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        # Cleanup
        pass
        #TODO consider
        # streamlit_process.terminate()




if __name__ == "__main__":
    main()