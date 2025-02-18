# Temp
# Pressure
# Humdity


from temperature_control.utils.test_utils import (
    fetch_humidity_test,
    fetch_temperature_measuring_test,
)


def get_reading_from_file(filename: str) -> str:
    with open(filename) as f:
        return f.read()


def round_reading(config: dict, reading: float) -> float:
    round(reading, config["db"]["round_decimal"])


def get_current_humidity(config: dict) -> float:
    # reading = get_reading_from_file(f"{config["execution_specs"]["i2c_device_base_path"]}/in_humidityrelative_input")
    # return round_reading(float(reading)/1000)
    return fetch_humidity_test()


def get_current_pressure(config: dict) -> float:
    # reading = get_reading_from_file(f"{config["execution_specs"]["i2c_device_base_path"]}/in_pressure_input")
    # return round_reading(float(reading)*10)
    return fetch_humidity_test()  # *10 hpa


def get_current_temperature(config: dict) -> float:
    # reading = get_reading_from_file(f"{config["execution_specs"]["i2c_device_base_path"]}/in_temp_input")
    # return round_reading(float(reading)/1000)
    return fetch_temperature_measuring_test(config["test_values"])
