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
    data_cache = []
    delta = 0
    # produce_test_log(run_config)

    # These dataframe will store a session's data
    if "df" not in st.session_state:
        st.session_state["df"] = fetch_latest_log()

    if "stat_df" not in st.session_state:
        st.session_state["stat_df"] = pd.DataFrame(columns=["mean", "median", "max"])

    # Initialize the app's layout
    st.title("Fan Control App")
    measure_metric_placeholder = st.empty()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        measure_metric_placeholder = st.empty()
    with col2:
        average_metric_placeholder = st.empty()
    with col3:
        median_metric_placeholder = st.empty()
    with col4:
        max_metric_placeholder = st.empty()

    measure_metric_placeholder.metric(label="Live Temperature", value=None)
    average_metric_placeholder.metric(  # TODO replace recent with interval
        label="Recent Average", value=None
    )
    median_metric_placeholder.metric(label="Recent Median", value=None)
    max_metric_placeholder.metric(label="Recent Max", value=None)
    line_chart_placeholder = st.empty()

    col5, col6, col7, col8 = st.columns(4)  # TODO replace
    with col5:
        cooling_placeholder_one = st.empty()
    with col6:
        cooling_placeholder_two = st.empty()
    with col7:
        cooling_placeholder_three = st.empty()
    with col8:
        cooling_placeholder_four = st.empty()

    cooling_placeholder_one.metric(label="cooling_placeholder", value=None)
    cooling_placeholder_two.metric(label="cooling_placeholder", value=None)
    cooling_placeholder_three.metric(label="cooling_placeholder", value=None)
    cooling_placeholder_four.metric(label="cooling_placeholder", value=None)

    # measure_metric_placeholder = st.empty()
    # stat_metric_placeholder = st.empty()

    # Main loop
    while True:
        datapoint = measure_temp(run_config, datapoint[1])

        st.session_state["df"] = append_df_with_new_data(
            st.session_state["df"], datapoint, run_config
        )

        # Data_cache
        data_cache.append(datapoint)  # TODO rework to dataframe

        # Create a new row for stats_df once there are sufficient data
        if len(data_cache) >= run_config["stats"]["sample_size"]:
            new_stat_row_dict, new_stat_row_df = build_new_stat_row(data_cache)
            # Append the new row to the existing stats_df
            st.session_state["stat_df"] = pd.concat(
                [st.session_state["stat_df"], new_stat_row_df]
            )  # TODO don't concat with empty df

            print(len(st.session_state["stat_df"]))  # TODO remove after testing

            # Clear the cache
            data_cache = []

        # Update UI
        measure_metric_placeholder.metric(
            label="Live Temperature",
            value=f"{datapoint[1]}°",
            delta=f"{delta}°",  # TODO implement delta
        )

        if len(st.session_state["stat_df"]) >= 1:
            average_metric_placeholder.metric(
                label="Recent Average", value=f"{new_stat_row_dict["mean"]}°"
            )
            median_metric_placeholder.metric(
                label="Recent Median", value=f"{new_stat_row_dict["median"]}°"
            )
            max_metric_placeholder.metric(
                label="Recent Max", value=f"{new_stat_row_dict["max"]}°"
            )

        if len(st.session_state["stat_df"]) >= 5:
            line_chart_placeholder.line_chart(
                data=st.session_state["stat_df"], x=None, y=["mean", "median", "max"]
            )  # TODO fetch from config

        # Clean up

        # Drop rows that are no longer needed from df, to prevent memory leak
        if len(st.session_state["stat_df"]) > 5:  # TODO adjust
            st.session_state["stat_df"] = st.session_state["stat_df"].tail(5)
            print(
                f"\n\n\n\n\n\n{len(st.session_state["stat_df"])}\n\n\n\n\n\n"
            )  # TODO remove after testing

        time.sleep(
            1
        )  # TODO time.sleep(run_config["execution_specs"]["update_interval"])


if __name__ == "__main__":
    run()
