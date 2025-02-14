from datetime import timedelta

import pandas as pd
import streamlit as st
from utils.general_utils import fetch_config

from temperature_control.utils.general_utils import (
    format_timestamp,
    get_timestamp,
)
from temperature_control.utils.sql_utils import execute_sql_to_df
from temperature_control.utils.streamlit_widgets import (
    check_password,
    get_cfg_widget,
    get_stat_widget,
)

if not check_password():
    st.stop()

# Main Streamlit app starts here

if "config" not in st.session_state:
    st.session_state["config"] = fetch_config()

if "stat_interval_df" not in st.session_state:
    st.session_state["stat_interval_df"] = pd.DataFrame()
    st.session_state["df_exists"] = False
    st.session_state["selector"] =  None
# else:
#     st.session_state["df_exists"] = True

# Initialize the app's layout with placeholders
st.title("Fan Control App")
measure_metric_placeholder = st.empty()
live_temp_col, recent_avg_col, recent_med_col, recent_max_col, live_humidity_col = st.columns(5, border=False,)
with live_temp_col:
    measure_metric_placeholder = st.empty()
with recent_avg_col:
    average_metric_placeholder = st.empty()
with recent_med_col:
    median_metric_placeholder = st.empty()
with recent_max_col:
    max_metric_placeholder = st.empty()
with live_humidity_col:
    live_humidity_placeholder = st.empty()

measure_metric_placeholder.metric(label="Live Temperature", value=None)
average_metric_placeholder.metric(
    label="Recent Average", value=None
)
median_metric_placeholder.metric(label="Recent Median", value=None)
max_metric_placeholder.metric(label="Recent Max", value=None)



# Create more human readable variable names for config: # TODO remove session state
db_config = st.session_state["config"]["db"]
db_name = st.session_state["config"]["db"]["db_name"]
table_name = st.session_state["config"]["db"]["table_name"]
timestamp_col = st.session_state["config"]["db"]["column_names"]["timestamp"]
temp_col = st.session_state["config"]["db"]["column_names"]["temperature"]
median_col = st.session_state["config"]["db"]["column_names"]["median"]
mean_col = st.session_state["config"]["db"]["column_names"]["mean"]
max_col = st.session_state["config"]["db"]["column_names"]["max"]
humidity_col = st.session_state["config"]["db"]["column_names"]["humidity"]

selector = "placeholder"

# Main loop

graph_tab, stats_tab, settings_tab = st.tabs(["Graph", "Stats", "Settings"])

with settings_tab:
    st.write("")
    get_cfg_widget()

with graph_tab:
    st.write("")
    line_chart_placeholder = st.empty()
    content_selector = "live_graph"

with stats_tab:
    st.write("")
    get_stat_widget()

while True:
    # Fetch Data from the desired analysis window:
    analysis_interval = get_timestamp() - timedelta(
        minutes=st.session_state["config"]["analysis_specs"]["interval_minutes"]
    )
    interval_datetime = format_timestamp(analysis_interval)
    interval_df = execute_sql_to_df( # specify columns
        db_name,
        f"SELECT * FROM {table_name} WHERE {timestamp_col} >= '{interval_datetime}'",
    )
    interval_df.sort_values(by=timestamp_col, ascending=True, inplace=True)

    latest_row = interval_df.iloc[[-1]]
    latest_reading = interval_df[temp_col].iloc[[-1]].item()
    if len(interval_df) >= 2:
        previous_reading = interval_df[temp_col].iloc[[-2]].item()
        delta = latest_reading - previous_reading
    else:
        delta = 0

    # Update placeholders
    recent_label = f"{st.session_state["config"]["analysis_specs"]["interval_minutes"]} minute"

    measure_metric_placeholder.metric(
        label="Live Temperature",
        value=f"{latest_reading}°C",
        delta=f"{delta}°C",
        delta_color="inverse",
    )

    average_metric_placeholder.metric(
        label=f"{recent_label} Average", value=f"{latest_row[mean_col].item()}°"
    )
    median_metric_placeholder.metric(
        label=f"{recent_label} Median", value=f"{latest_row[median_col].item()}°"
    )
    max_metric_placeholder.metric(
        label=f"{recent_label} Max", value=f"{latest_row[max_col].item()}°"
    )
    live_humidity_placeholder.metric(
        label="Live Humidity",
        value=f"{latest_row[humidity_col].item()}%"
    )
    if len(interval_df) > 5 and content_selector == "live_graph":
        interval_df["activation_threshold"] = st.session_state["config"][
            "temperature_thresholds"
        ]["activation_threshold"]
        line_chart_placeholder.line_chart(
            data=interval_df, x=None, y=[temp_col, "activation_threshold"]
        )