# Temp
# Pressure
# Humdity


from measuring_assets.test_prop import (
    fetch_humidity_test,
    fetch_temperature_measuring_test,
)


def get_current_humidity():
    return fetch_humidity_test()
    # /1000


def get_current_pressure():
    pass  # *10 hpa


def get_current_temperature(config: dict) -> float:
    # /1000
    return fetch_temperature_measuring_test(config["test_values"])
