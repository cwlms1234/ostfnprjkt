import logging
import time
import subprocess
import duckdb
import glob

import pandas as pd

from measuring_assets.measuring import (
    measure_temp,
)
from utils import fetch_config

run_config = fetch_config()

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

def collect_data():
    """Collects temperature data."""
    return measure_temp(run_config)

def insert_data(con, table_name, data):
    """Inserts data into the DuckDB table."""
    logger.info(f"*** INSERT INTO {table_name} VALUES {data}") # TODO remove
    con.execute(f"INSERT INTO {table_name} VALUES (?, ?)", data)

def delete_table(con, table_name):
    con.execute(f"DROP TABLE IF EXISTS {table_name}")
    
def main():

    ### Initialize DuckDB:
    db_cfg = run_config["duck_db"]
    table_name = db_cfg["table_name"]

    # Create Connection
    con = duckdb.connect(db_cfg["con_name"])
    logger.info(f"*** Connecting via {con}") # TODO remove
    
    #Create Table
    column_string = ", ".join(db_cfg["columns"])

    delete_table(con, table_name)
    con.execute(f"CREATE TABLE {table_name} ({column_string})")
    
    # Allow delay for DuckDB initialization
    time.sleep(2)

    # Start the Streamlit app
    subprocess.Popen(["streamlit", "run", "src/entrypoint.py"])
    
    try: 
        while True:
            data = collect_data()
            insert_data(con, table_name, data)
            time.sleep(5) # get from config
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        # Cleanup
        delete_table(con, table_name)
        con.close()
        #TODO consider
        # streamlit_process.terminate()




if __name__ == "__main__":
    main()