import random
from datetime import datetime, timedelta

from src.measuring_assets.utils.measuring_utils import write_to_file


def fetch_temperature_measuring_test(test_dict: dict, last_value: int = 20) -> int:
    min_limit = test_dict["lower"]
    max_limit = test_dict["upper"]

    lower_border = last_value - 5
    rand_min = min_limit if lower_border <= min_limit else lower_border

    upper_border = last_value + 5
    rand_max = max_limit if upper_border >= max_limit else upper_border

    return random.randrange(rand_min, rand_max, 1)

def produce_test_log(): # python -c 'from src.measuring_assets.test_prop import produce_test_log; produce_test_log()'  # noqa: E501
    timestamp = datetime.now()
    time_cursor = timestamp - timedelta(days=1)
    while time_cursor < timestamp:
        time_cursor += timedelta(seconds=30)
        temp_measure = fetch_temperature_measuring_test({"upper": 70, "lower": 20})
        write_to_file({"csv_folder_path": "logs/"},(time_cursor, temp_measure))