import statistics


def unpack_query_result(query_result: list[tuple]) -> list:
    return [row[0] for row in query_result]


def calculate_interval_stats(config: dict, interval_temps: list) -> dict:
    """Takes a list of recent measurements and returns a tuple of statistical metrics based on that list"""
    print(f"interval_temps = {interval_temps}")  # TODO remove
    mean_temp = statistics.mean(interval_temps)
    mean_temp = round(mean_temp, 1)
    median_temp = statistics.median(interval_temps)
    max_temp = max(interval_temps)
    return {
        config["sqlite"]["column_names"]["mean"]: mean_temp,
        config["sqlite"]["column_names"]["median"]: median_temp,
        config["sqlite"]["column_names"]["max"]: max_temp,
    }


def toggle_pump(cfg: dict, data: dict) -> None:
    """Compare the current temperature to the activation / deactivation threshold and toggle the pump accordingly"""
    reading_col = cfg["sqlite"]["column_names"]["reading"]
    if data[reading_col] >= cfg["temperature_thresholds"]["activation_threshold"]:
        print(
            f"*** Measured {data[reading_col]} >= {cfg["temperature_thresholds"]["activation_threshold"]} \n Powering pump"
        )
    elif data[reading_col] <= cfg["temperature_thresholds"]["activation_threshold"]:
        print(
            f"*** Measured {data[reading_col]} >= {cfg["temperature_thresholds"]["deactivation_threshold"]} \n Shutting down pump"
        )
    else:
        pass
