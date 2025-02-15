# Temp
# Pressure
# Humdity


from temperature_control.utils.test_utils import (
    fetch_humidity_test,
    fetch_temperature_measuring_test,
)

def get_reading_from_file(filename:str) -> str:
    with open(filename, "r") as f:
        return f.read()


def get_current_humidity():
    # reading = get_reading_from_file("sys/bus/iio:device0/in_humidityrelative_input")
    # return float(reading)/1000
    return fetch_humidity_test()


def get_current_pressure():
    # reading = get_reading_from_file("/sys/bus/iio/devices/iio:device0/in_pressure_input")
    # return float(reading)*10
    return fetch_humidity_test()  # *10 hpa


def get_current_temperature(config: dict) -> float:
    # reading = get_reading_from_file("sys/bus/iio/devices/iio:device0_in_temp_input")
    # return float(reading)/1000
    return fetch_temperature_measuring_test(config["test_values"])

