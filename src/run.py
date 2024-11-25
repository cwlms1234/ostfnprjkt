import time

import pandas as pd
import streamlit as st
from measuring_assets.measuring import (
    append_df_with_new_data,
    build_new_stat_row,
    measure_temp,
)
from measuring_assets.utils.measuring_utils import fetch_latest_log
from utils import fetch_config


def run():
    datapoint = ("timestamp", 25)  # TODO remove after testing
    run_config = fetch_config()
    stats_df = pd.DataFrame(columns=["mean", "median", "max"])
    data_cache = []
    delta = None
    # produce_test_log(run_config)

    if "df" not in st.session_state:
        st.session_state["df"] = fetch_latest_log()

    st.title("Fan Control App")
    measure_metric_placeholder = st.empty()
    stat_metric_placeholder = st.empty()

    while True:
        datapoint = measure_temp(run_config, datapoint[1])

        measure_metric_placeholder.metric(
            label="Live Temperature", value=f"{datapoint[1]}°", delta=f"{delta}°"
        )

        st.session_state["df"] = append_df_with_new_data(
            st.session_state["df"], datapoint, run_config
        )

        data_cache.append(datapoint)
        # Create a new row for stats_df once there are sufficient data
        if len(data_cache) >= run_config["stats"]["sample_size"]:
            new_stat_row_dict, new_stat_row_df = build_new_stat_row(data_cache)
            # Append the new row to the existing stats_df
            stats_df = pd.concat(
                [stats_df, new_stat_row_df]
            )  # TODO don't concat with empty df

            print(stats_df)  # TODO remove after testing

            stat_metric_placeholder.metric(
                label="Recent Average", value=f"{new_stat_row_dict["mean"]}°"
            )

            # Clear the cache
            data_cache = []

        if len(stats_df) >= 5:
            pass  # TODO draw chart
        time.sleep(
            5
        )  # TODO time.sleep(run_config["execution_specs"]["update_interval"])


if __name__ == "__main__":
    run()


# DUCK DB Testing
# if "db_con" not in st.session_state:
#    st.session_state["db_con"] = duckdb.connect("logs/temp_app.db")
#
##datapoint = measure_temp(run_config, datapoint[1])
# df = st.session_state["db_con"].sql("SELECT * FROM readings").df()
# df
