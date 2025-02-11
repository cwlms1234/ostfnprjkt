from datetime import datetime, time

import pandas as pd
import streamlit as st
from utils.general_utils import fetch_config, write_config
from utils.plots import create_heatmap_plot
from utils.sql_utils import execute_sql_select, execute_sql_to_df

from temperature_control.utils.plots import (
    create_pump_diagram,
    create_temperature_distribution_chart,
)

if "download_df" not in st.session_state:
    st.session_state["download_df"] = pd.DataFrame()
    st.session_state["df_exists"] = False
else:
    st.session_state["df_exists"] = True

preview_df = False
plotly_chart = False
executed_search = False

st.session_state["config"] = fetch_config()

# Create more human readable variable names for config:
db_config = st.session_state["config"]["db"]
db_name = st.session_state["config"]["db"]["db_name"]
table_name = st.session_state["config"]["db"]["table_name"]
timestamp_col = st.session_state["config"]["db"]["column_names"]["timestamp"]
temp_col = st.session_state["config"]["db"]["column_names"]["temperature"]
median_col = st.session_state["config"]["db"]["column_names"]["median"]
mean_col = st.session_state["config"]["db"]["column_names"]["mean"]
max_col = st.session_state["config"]["db"]["column_names"]["max"]

# Fetch timestamp boundaries for selection boxes
query_oldest = f"""SELECT {timestamp_col} 
                    FROM {table_name} 
                    ORDER BY {timestamp_col} 
                    ASC LIMIT 1"""
query_newest = f"""SELECT {timestamp_col}
                    FROM {table_name} 
                    ORDER BY {timestamp_col}
                    DESC LIMIT 1"""
oldest_timestamp_str = execute_sql_select(
    db_name, query_oldest, unpack_first_value=True
)
newest_timestamp_str = execute_sql_select(
    db_name, query_newest, unpack_first_value=True
)
# Convert timestamp from string to datetime
oldest_timestamp = datetime.fromisoformat(oldest_timestamp_str)
newest_timestamp = datetime.fromisoformat(newest_timestamp_str)


st.write(
    f"Select interval between {newest_timestamp.date()} and {oldest_timestamp.date()} for CSV download."
)
start_date = st.date_input(
    label="Start Date",
    min_value=oldest_timestamp,
    max_value=newest_timestamp,
)
end_date = st.date_input(
    label="End Date",
    min_value=oldest_timestamp,
    max_value=newest_timestamp,
)

# TODO select weekday and maybe hour:
# values = range(5)
# labels = ['first','second','third','fourth','fifth']

# selection = st.select_slider('Choose a range',values,value=(1,3), format_func=(lambda x:labels[x]))

# st.write(f'The selection is {selection} with values having type {type(selection[0])}.')

###

# Make sure single day queries return data
if start_date == end_date:
    start_date = datetime.combine(start_date, time.min)
    end_date = datetime.combine(
        end_date, time.max
    )  # TODO use actual timestamp if this is set to current date

# Set up button row
left_stat_button, middle_stat_button, right_stat_button = st.columns(spec=3)

with left_stat_button:  # TODO adjust select to be more specific than *
    if st.button(label="Execute Search", use_container_width=True):
        query = f"""SELECT * 
                    FROM {table_name} 
                    WHERE {timestamp_col} >= '{start_date}' 
                    AND {timestamp_col} <= '{end_date}'"""
        st.session_state["download_df"] = execute_sql_to_df(db_name, query)
        executed_search = True
        # st.success(f"Query fechted {len(st.session_state['download_df'])} lines!")

    if st.button(
        label="Show Heatmap",
        use_container_width=True,
        disabled=not st.session_state["df_exists"],
    ):
        plotly_chart = create_heatmap_plot(
            st.session_state["download_df"], st.session_state["config"]
        )

with middle_stat_button:
    if st.button(
        label="Preview Data",
        use_container_width=True,
        disabled=not st.session_state["df_exists"],
    ):
        preview_df = True

    if st.button(
        label="Show Temp Distribution",
        use_container_width=True,
        disabled=not st.session_state["df_exists"],
    ):
        plotly_chart = create_temperature_distribution_chart(
            st.session_state["download_df"], st.session_state["config"]
        )

with right_stat_button:
    st.download_button(
        label="Download as CSV",  # TODO round filename if 1 day interval
        data=st.session_state["download_df"].to_csv().encode("utf-8"),
        file_name=f"{start_date}_{end_date}.csv",
        mime="text/csv",
        use_container_width=True,
        disabled=not st.session_state["df_exists"],
    )

    if st.button(
        label="Show Pump Uptime",
        use_container_width=True,
        disabled=not st.session_state["df_exists"],
    ):
        plotly_chart = create_pump_diagram(
            st.session_state["download_df"], st.session_state["config"]
        )

if preview_df:
    st.dataframe(data=st.session_state["download_df"], use_container_width=True)

if plotly_chart:
    st.plotly_chart(figure_or_data=plotly_chart, use_container_width=True)

if executed_search:
    st.success(f"Query fechted {len(st.session_state['download_df'])} lines!")

st.markdown("#")


with st.expander(label="Adjust config:"):
    st.write("Measuring Parameters:")

    top_left_cfg_button, top_middle_cfg_button, top_right_cfg_button = st.columns(
        [1, 1, 1]
    )
    with top_left_cfg_button:
        update_frequency_minutes = st.number_input(
            label="Update interval (minutes)",
            step=0.5,
            value=float(
                (st.session_state["config"]["execution_specs"]["update_frequency"]) / 60
            ),
        )
        st.session_state["config"]["execution_specs"]["update_frequency"] = (
            update_frequency_minutes * 60
        )

    with top_middle_cfg_button:
        min_threshold = st.number_input(
            label="Deactivation Threshold (°C)",
            step=1,
            value=st.session_state["config"]["temperature_thresholds"][
                "deactivation_threshold"
            ],
        )
        st.session_state["config"]["temperature_thresholds"][
            "deactivation_threshold"
        ] = min_threshold

    with top_right_cfg_button:
        max_threshold = st.number_input(
            label="Activation Threshold (°C)",
            step=1,
            value=st.session_state["config"]["temperature_thresholds"][
                "activation_threshold"
            ],
        )
        st.session_state["config"]["temperature_thresholds"]["activation_threshold"] = (
            max_threshold
        )

    st.write("Monitoring Parameters:")

    middle_left_cfg_button, middle_middle_cfg_button, middle_right_cfg_button = (
        st.columns([1, 1, 1])
    )
    with middle_left_cfg_button:
        warning_limit = st.number_input(
            label="Warning value (°C)",
            step=1,
            value=st.session_state["config"]["temperature_thresholds"]["warning_limit"],
        )
        st.session_state["config"]["temperature_thresholds"]["warning_limit"] = (
            warning_limit
        )
    with middle_middle_cfg_button:
        alert_limit = st.number_input(
            label="Alert value (°C)",
            step=1,
            value=st.session_state["config"]["temperature_thresholds"]["alert_limit"],
        )
        st.session_state["config"]["temperature_thresholds"]["alert_limit"] = (
            alert_limit
        )
    with middle_right_cfg_button:
        pass

    bottom_left_cfg_button, bottom_right_cfg_button = st.columns(2)
    with bottom_left_cfg_button:
        if st.button(label="Write to config", use_container_width=True):
            print(st.session_state["config"])
            write_config(st.session_state["config"])
    with bottom_right_cfg_button:
        if st.button(label="Load default config", use_container_width=True):
            write_config(fetch_config("default_config.yaml"))

# TODO make layout prettier
# TODO add value parameter based on config to number input
# TODO read config on every loop in data_collector
