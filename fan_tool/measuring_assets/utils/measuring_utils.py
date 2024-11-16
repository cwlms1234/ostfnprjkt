import csv
from datetime import datetime
import os
import pytz

def get_timestamp():
    # Get the current time in the Berlin time zone 
    berlin_tz = pytz.timezone('Europe/Berlin') 
    return datetime.now(berlin_tz).strftime("%d-%m-%Y %H:%M:%S")

def get_date():
    berlin_tz = pytz.timezone('Europe/Berlin') 
    return datetime.now(berlin_tz).strftime("%d-%m-%Y")

def write_to_file(execution_specs, data):

    # Create specified file path if it doesn't already exist
    os.makedirs(execution_specs["csv_folder_path"], exist_ok=True)

    # Returns the current YYYY-MM-DD, so there will be new log file each day
    date = get_date()

    with open(f"{execution_specs["csv_folder_path"]}/{date}.csv", "a", newline="") as file:
        writer = csv.writer(file)
        # Determine whether the file already exists:
        if not file.tell():
            writer.writerow(("Time", "Reading"))
        else:
            pass
        writer.writerow(data)
