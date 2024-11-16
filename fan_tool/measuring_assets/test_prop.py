import random


def fetch_temperature_measuring_test(last_value: int,test_dict: dict) -> int:
    min_limit = test_dict["lower"]
    max_limit = test_dict["upper"]

    lower_border = last_value - 5
    if lower_border <= min_limit:
        rand_min = min_limit
    else:
        rand_min = lower_border

    upper_border = last_value + 5
    if upper_border >= max_limit:
        rand_max = max_limit
    else:
        rand_max = upper_border

    return random.randrange(rand_min, rand_max, 1)