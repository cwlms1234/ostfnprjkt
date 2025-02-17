import statistics


def unpack_query_result(query_result: list[tuple]) -> list:
    """Unpack query result for simpler downstream handing"""
    return [row[0] for row in query_result]


def calculate_interval_stats(db_cfg: dict, interval_temps: list) -> dict:
    """Takes a list of recent measurements and returns a dict of statistical metrics based on that list"""
    mean_temp = statistics.mean(interval_temps)
    mean_temp = round(mean_temp, db_cfg["round_decimal"])
    median_temp = statistics.median(interval_temps)
    max_temp = max(interval_temps)
    return {
        db_cfg["column_names"]["mean"]: mean_temp,
        db_cfg["column_names"]["median"]: median_temp,
        db_cfg["column_names"]["max"]: max_temp,
    }


def toggle_pump(cfg: dict, data: dict, previous_run: bool | None) -> bool:
    """Compare the current temperature to the activation / deactivation threshold and toggle the pump accordingly"""
    col_names = cfg["db"]["column_names"]
    return bool(
        data[col_names["temperature"]]
        >= cfg["temperature_thresholds"]["activation_threshold"]
        or data[col_names["temperature"]]
        >= cfg["temperature_thresholds"]["deactivation_threshold"]
        and previous_run == True
    )
