

from measuring_assets.test_prop import fetch_temperature_measuring_test
from measuring_assets.utils.measuring_utils import get_timestamp, write_to_file


def measure_temp(config: dict, temp_measure: int) -> int:
    if not temp_measure: temp_measure = 25
    temp_measure = fetch_temperature_measuring_test(temp_measure, config["test_values"])
    timestamp = get_timestamp()
    print(
        f"\nMeasured {temp_measure} degrees Celsius at {timestamp}"
    )
    data = (timestamp, temp_measure)


    write_to_file(config["execution_specs"], data)




    return temp_measure
    #time.sleep(5)
    #time.sleep(config["execution_specs"].update_interval)
