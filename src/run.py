from measuring_assets.measuring import measure_temp
from utils import fetch_config


def run():
    temp = 25  # TODO remove after testing
    run_config = fetch_config()
    measure_temp(run_config, temp)


if __name__ == "__main__":
    run()
