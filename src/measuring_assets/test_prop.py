import random

#from .utils.measuring_utils import get_timestamp, write_to_file


def fetch_temperature_measuring_test(test_dict: dict) -> int:
    """ Fetch a random int to simulate a temperature reading"""
    min_limit = test_dict["lower"]
    max_limit = test_dict["upper"]

    return random.randrange(min_limit, max_limit, 1)

