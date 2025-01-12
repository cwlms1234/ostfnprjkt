import logging
import sqlite3 as sql
import subprocess
import time

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

def execute_sql(db_name, statement):
    try:
        with sql.connect(db_name) as conn:
            conn.execute(statement)
    except sql.OperationalError as e:
        logger.error("Failed to open database:", e)
        


def collect_data():
    """Collects temperature data."""
    return measure_temp(run_config)

def insert_data(db_name, table_name, data):
    """Inserts data into the DuckDB table."""
    logger.info(f"*** INSERT INTO {db_name} VALUES {data}") # TODO remove
    execute_sql(db_name, f"INSERT INTO {table_name} VALUES ('{data[0]}', {data[1]})")

def delete_table(con, db_name):
    con.execute(f"DROP TABLE IF EXISTS {db_name}")
    
def main():

    ### Initialize DuckDB:
    db_cfg = run_config["sqlite"]
    db_name = db_cfg["db_name"]

    
    #Create Table
    column_string = ", ".join(db_cfg["table_columns"])
    create_statement = f"CREATE TABLE IF NOT EXISTS {db_cfg["table_name"]} ({column_string})"
    execute_sql(db_cfg["db_name"], create_statement)



    
    # Allow delay for DuckDB initialization
    time.sleep(2)

    # Start the Streamlit app
    subprocess.Popen(["streamlit", "run", "src/entrypoint.py"])
    
    try: 
        while True:
            data = collect_data()
            insert_data(db_cfg["db_name"], db_cfg["table_name"], data)
            time.sleep(5) # get from config
    except Exception as e:
        logger.error(f"Error occurred: {e}")
    finally:
        # Cleanup
        pass
        #delete_table(con, table_name)
        #con.close()
        #TODO consider
        # streamlit_process.terminate()




if __name__ == "__main__":
    main()