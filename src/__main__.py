from measuring_assets.measuring import measure_temp
from utils import fetch_config

run_config = fetch_config()

temp = 25


measure_temp(run_config, temp)