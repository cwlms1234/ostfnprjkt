#import csv
#import os
from datetime import datetime

#import pandas as pd
import pytz


def get_timestamp() -> datetime:
    """Get the current time in the Berlin time zone"""
    berlin_tz = pytz.timezone("Europe/Berlin")
    timestamp = datetime.now(berlin_tz)
    return format_timestamp(timestamp)

def format_timestamp(timestamp: datetime) -> datetime:
    """Return the current time in the Berlin time zone"""
    return timestamp.replace(
        hour=timestamp.hour,
        minute=timestamp.minute,
        second=timestamp.second,
        microsecond=0,
    )


def get_date():
    """Get the current year and month"""
    berlin_tz = pytz.timezone("Europe/Berlin")
    return datetime.now(berlin_tz).strftime("%m-%Y")


# def get_last_n_months_files(n): #TODO probably delete
#     """Get the csv files for the last n months, including the current"""
#     last_n_months = []
#     date = datetime.today()
#     year = date.year
#     month = date.month
#     while len(last_n_months) < n:
#         last_n_months.append(f"{month}-{year}.csv")
#         month, year = get_last_month(month, year)
#     return last_n_months


# def get_last_month(month, year): #TODO probably delete
#     """"""
#     if month == 1:
#         last_month = 12
#         last_year = year - 1
#     else:
#         last_month = month - 1
#         last_year = year
#     return (last_month, last_year)


# def fetch_latest_log() -> pd.DataFrame: #TODO probably delete
#     date = get_date()
#     filename = f"logs/{date}.csv"
#     if os.path.exists(filename):
#         return pd.read_csv(filename).set_index("Time")


# def write_to_file(config, data) -> None: #TODO probably delete
#     # Create specified file path if it doesn't already exist
#     os.makedirs(config["execution_specs"]["csv_folder_path"], exist_ok=True)

#     # Returns the current YYYY-MM, so there will be new log file each month
#     date = get_date()

#     with open(
#         f"{config["execution_specs"]["csv_folder_path"]}/{date}.csv", "a", newline=""
#     ) as file:
#         writer = csv.writer(file)
#         # Determine whether the file already exists:
#         if not file.tell():
#             writer.writerow(
#                 (config["csv_headers"]["timestamp"], config["csv_headers"]["reading"])
#             )
#         else:
#             pass
#         writer.writerow(data)

# TODO remove obsolete config options after deleting and clean up imports