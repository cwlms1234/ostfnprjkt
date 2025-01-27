import statistics

import pandas as pd

from measuring_assets.test_prop import fetch_temperature_measuring_test
from measuring_assets.utils.measuring_utils import get_timestamp  #, write_to_file


def measure_temp(config: dict) -> int:
    temp_measure = fetch_temperature_measuring_test(config["test_values"])
    timestamp = get_timestamp()
    print(
        f"\nMeasured {temp_measure} degrees Celsius at {timestamp}"
    )  # TODO consider removing
    data = (timestamp, temp_measure)

    #write_to_file(config, data) # TODO consider removing

    return data


def build_new_stat_row(data_list: list) -> pd.DataFrame: # TODO probably remove
    # Find out the borders of the interval
    timestamps_list = [item[0] for item in data_list]
    index = max(timestamps_list)

    # Find mean, median and max values
    measure_list = [item[1] for item in data_list]
    mean_value = statistics.mean(measure_list)  # noqa: F821
    median_value = statistics.median(measure_list)
    max_value = max(measure_list)

    new_row_dict = {"mean": mean_value, "median": median_value, "max": max_value}

    # Combine the values into a new row
    new_row_df = pd.DataFrame(
        new_row_dict,
        index=[index],
    )

    return new_row_dict, new_row_df


def append_df_with_new_data(df: pd.DataFrame, measurement: tuple, config: dict): # TODO probably remove
    new_row = pd.DataFrame(
        {config["csv_headers"]["reading"]: measurement[1]}, index=[measurement[0]]
    )

    return pd.concat([df, new_row])
