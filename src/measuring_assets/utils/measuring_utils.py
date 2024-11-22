import csv
import os
from datetime import datetime, timedelta

import pytz


def get_timestamp():
    # Get the current time in the Berlin time zone
    berlin_tz = pytz.timezone("Europe/Berlin")
    return datetime.now(berlin_tz).strftime("%d-%m-%Y %H:%M:%S")


def get_date():
    # Get the current year and month
    berlin_tz = pytz.timezone("Europe/Berlin")
    return datetime.now(berlin_tz).strftime("%m-%Y")


def get_last_n_months_files(n):
    # Get the csv files for the last n months, including the current
    last_n_months = []
    date = datetime.today()
    year = date.year
    month = date.month
    while len(last_n_months) < n:
        last_n_months.append(f"{month}-{year}.csv")
        month, year = get_last_month(month, year)
    return last_n_months


def get_last_month(month, year):
    if month == 1:
        last_month = 12
        last_year = year - 1
    else:
        last_month = month - 1
        last_year = year
    return (last_month, last_year)


def write_to_file(config, data):
    # Create specified file path if it doesn't already exist
    os.makedirs(config["execution_specs"]["csv_folder_path"], exist_ok=True)

    # Returns the current YYYY-MM, so there will be new log file each month
    date = get_date()

    with open(
        f"{config["execution_specs"]["csv_folder_path"]}/{date}.csv", "a", newline=""
    ) as file:
        writer = csv.writer(file)
        # Determine whether the file already exists:
        if not file.tell():
            writer.writerow(
                (config["csv_headers"]["timestamp"], config["csv_headers"]["reading"])
            )
        else:
            pass
        writer.writerow(data)
