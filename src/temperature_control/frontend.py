from datetime import datetime, timedelta, time
import hmac
import pandas as pd

import streamlit as st
from temperature_control.utils.general_utils import format_timestamp, get_timestamp, write_config
from temperature_control.utils.plots import create_heatmap_plot, create_pump_diagram, create_temperature_distribution_chart
from temperature_control.utils.sql_utils import execute_sql_select, execute_sql_to_df
from temperature_control.utils.streamlit_utils import check_password, get_cfg_widget
from utils.general_utils import fetch_config, fetch_src_file_path



if not check_password():
    st.stop()

# Main Streamlit app starts here

if "config" not in st.session_state:
    st.session_state["config"] = fetch_config()


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
median_metric_placeholder.metric(label=f"Recent Median", value=None)
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

selector = None

# Main loop

graph_tab, tab2, settings_tab = st.tabs(["Graph", "Stats", "Settings"])
with settings_tab:
    get_cfg_widget()

with graph_tab:
    line_chart_placeholder = st.empty()
    selector = "live_graph"

with tab2:
    pass


# live_graph_col, stat_col, settings_col = st.columns(3)
# with live_graph_col:
#     if st.button(
#         key="live graph",
#         label="Show Live Graph",
#         use_container_width=True,
#     ):
#         selector = "live_graph"
# with stat_col:
#     if st.button(
#         key="stats",
#         label="Show Stat Options",
#         use_container_width=True,
#     ):
#         selector = "stats"
# with settings_col:
#     if st.button(
#         key="settings", 
#         label="Show Settings",
#         use_container_width=True,
#     ):
#         selector = "settings"



# if selector == "settings":
#     st.write("Measuring Parameters:")

#     top_left_cfg_button, top_middle_cfg_button, top_right_cfg_button = st.columns(3)
#     with top_left_cfg_button:
#         update_frequency_minutes = st.number_input(
#             label="Update interval (minutes)",
#             step=0.5,
#             value=float(
#                 (st.session_state["config"]["execution_specs"]["update_frequency"]) / 60
#             ),
#         )
#         st.session_state["config"]["execution_specs"]["update_frequency"] = (
#             update_frequency_minutes * 60
#         )

#     with top_middle_cfg_button:
#         min_threshold = st.number_input(
#             label="Deactivation Threshold (°C)",
#             step=1,
#             value=st.session_state["config"]["temperature_thresholds"][
#                 "deactivation_threshold"
#             ],
#         )
#         st.session_state["config"]["temperature_thresholds"][
#             "deactivation_threshold"
#         ] = min_threshold

#     with top_right_cfg_button:
#         max_threshold = st.number_input(
#             label="Activation Threshold (°C)",
#             step=1,
#             value=st.session_state["config"]["temperature_thresholds"][
#                 "activation_threshold"
#             ],
#         )
#         st.session_state["config"]["temperature_thresholds"]["activation_threshold"] = (
#             max_threshold
#         )

#     st.write("Monitoring Parameters:")

#     middle_left_cfg_button, middle_middle_cfg_button, middle_right_cfg_button = (
#         st.columns([1, 1, 1])
#     )
#     with middle_left_cfg_button:
#         warning_limit = st.number_input(
#             label="Warning value (°C)",
#             step=1,
#             value=st.session_state["config"]["temperature_thresholds"]["warning_limit"],
#         )
#         st.session_state["config"]["temperature_thresholds"]["warning_limit"] = (
#             warning_limit
#         )
#     with middle_middle_cfg_button:
#         alert_limit = st.number_input(
#             label="Alert value (°C)",
#             step=1,
#             value=st.session_state["config"]["temperature_thresholds"]["alert_limit"],
#         )
#         st.session_state["config"]["temperature_thresholds"]["alert_limit"] = (
#             alert_limit
#         )
#     with middle_right_cfg_button:
#         pass

#     bottom_left_cfg_button, bottom_right_cfg_button = st.columns(2)
#     with bottom_left_cfg_button:
#         if st.button(label="Write to config", use_container_width=True):
#             print(st.session_state["config"])
#             write_config(st.session_state["config"])
#     with bottom_right_cfg_button:
#         if st.button(label="Load default config", use_container_width=True):
#             write_config(fetch_config("default_config.yaml"))

# elif selector == "live_graph":
#     line_chart_placeholder = st.empty()

# elif selector == "stats":
#     pass 

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
        label=f"Live Humidity",
        value=f"{latest_row[humidity_col].item()}%"
    )
    if len(interval_df) > 5 and selector == "live_graph":
        interval_df["activation_threshold"] = st.session_state["config"][
            "temperature_thresholds"
        ]["activation_threshold"]
        line_chart_placeholder.line_chart(
            data=interval_df, x=None, y=[temp_col, "activation_threshold"]
        )