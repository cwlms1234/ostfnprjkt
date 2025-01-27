import random

#from .utils.measuring_utils import get_timestamp, write_to_file


def fetch_temperature_measuring_test(test_dict: dict) -> int:
    """ Fetch a random int to simulate a temperature reading"""
    min_limit = test_dict["lower"]
    max_limit = test_dict["upper"]

    return random.randrange(min_limit, max_limit, 1)


# def produce_test_log( # TODO probably remove
#     config,
# ):  # python -c 'from src.measuring_assets.test_prop import produce_test_log; produce_test_log()'  # noqa: E501
#     timestamp = get_timestamp()
#     time_cursor = timestamp - timedelta(days=1)
#     while time_cursor < timestamp:
#         time_cursor += timedelta(seconds=30)
#         temp_measure = fetch_temperature_measuring_test({"upper": 70, "lower": 20})
#         write_to_file(
#             config,
#             (time_cursor, temp_measure),
#         )
