import time
from datetime import timedelta

import streamlit as st

from utils.general_utils import format_timestamp, get_timestamp
from utils.sql_utils import execute_sql_to_df

# produce_test_log(run_config)


# Initialize the app's layout with placeholders
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


# Create more human readable variable names for config:
db_config = st.session_state["config"]["db"]
db_name = st.session_state["config"]["db"]["db_name"]
table_name = st.session_state["config"]["db"]["table_name"]
timestamp_col = st.session_state["config"]["db"]["column_names"]["timestamp"]
reading_col = st.session_state["config"]["db"]["column_names"]["temperature"]
median_col = st.session_state["config"]["db"]["column_names"]["median"]
mean_col = st.session_state["config"]["db"]["column_names"]["mean"]
max_col = st.session_state["config"]["db"]["column_names"]["max"]

# Main loop
while True:
    # Fetch Data from the desired analysis window:
    analysis_interval = get_timestamp() - timedelta(
        minutes=st.session_state["config"]["analysis_specs"]["interval_minutes"]
    )
    interval_datetime = format_timestamp(analysis_interval)
    interval_df = execute_sql_to_df(
        db_name,
        f"SELECT * FROM {table_name} WHERE {timestamp_col} >= '{interval_datetime}'",
    )
    interval_df.sort_values(by=timestamp_col, ascending=True, inplace=True)

    latest_row = interval_df.iloc[[-1]]
    latest_reading = interval_df[reading_col].iloc[[-1]].item()
    if len(interval_df) >= 2:
        previous_reading = interval_df[reading_col].iloc[[-2]].item()
        delta = latest_reading - previous_reading
    else:
        delta = 0

    # Update placeholders
    measure_metric_placeholder.metric(
        label="Live Temperature",
        value=f"{latest_reading}°C",
        delta=f"{delta}°C",
        delta_color="inverse",
    )

    average_metric_placeholder.metric(
        label="Recent Average", value=f"{latest_row[mean_col].item()}°"
    )
    median_metric_placeholder.metric(
        label="Recent Median", value=f"{latest_row[median_col].item()}°"
    )
    max_metric_placeholder.metric(
        label="Recent Max", value=f"{latest_row[max_col].item()}°"
    )

    if len(interval_df) > 5:
        line_chart_placeholder.line_chart(
            data=interval_df, x=None, y=[mean_col, median_col, max_col]
        )  # TODO fetch from config

    time.sleep(6)  # TODO time.sleep(run_config["execution_specs"]["update_frequency"])
