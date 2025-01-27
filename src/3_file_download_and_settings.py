from datetime import datetime, time

import pandas as pd
import streamlit as st

from utils import execute_sql_select, execute_sql_to_df

if "download_df" not in st.session_state:
    st.session_state["download_df"] = pd.DataFrame()

preview_df = False

# Create more human readable variable names for config:
db_config = st.session_state["config"]["sqlite"]
db_name = st.session_state["config"]["sqlite"]["db_name"]
table_name = st.session_state["config"]["sqlite"]["table_name"]
timestamp_col = st.session_state["config"]["sqlite"]["column_names"]["timestamp"]
reading_col = st.session_state["config"]["sqlite"]["column_names"]["reading"]
median_col = st.session_state["config"]["sqlite"]["column_names"]["median"]
mean_col = st.session_state["config"]["sqlite"]["column_names"]["mean"]
max_col = st.session_state["config"]["sqlite"]["column_names"]["max"]

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

# Make sure single day queries return data
if start_date == end_date:
    start_date = datetime.combine(start_date, time.min)
    end_date = datetime.combine(end_date, time.max) # TODO use actual timestamp if this is set to current date

# Set up button row
col1, col2, col3 = st.columns(spec=3)

with col1:
    if st.button(label="Execute Search"):
        query = f"""SELECT * 
                    FROM {table_name} 
                    WHERE {timestamp_col} >= '{start_date}' 
                    AND {timestamp_col} <= '{end_date}'"""
        st.session_state["download_df"] = execute_sql_to_df(db_name, query)
        st.success(f"Query fechted {len(st.session_state["download_df"])} lines!")

with col2:
    if st.button(label="Preview Data"):
        preview_df = True

with col3:
    st.download_button(
        label="Download as CSV",
        data=st.session_state["download_df"].to_csv().encode("utf-8"),
        file_name=f"{start_date}_{end_date}.csv",
        mime="text/csv",
    )

if preview_df:
    st.dataframe(data=st.session_state["download_df"], use_container_width=True)

st.markdown('#')


with st.expander(label="Adjust config:"):

    st.write("Adjust config.")

    col4, col5, col6 = st.columns([1,1,1])
    with col4:
        st.number_input(label="Select update interval in minutes.", step=0.5)

    with col5:
        st.number_input(label="Min value",step=1)

    with col6:
        st.number_input(label="Max_value.",step=1)

    st.write("Monitoring parameters:")

    col7, col8, col9 = st.columns([1,1,1])
    with col7:
        st.number_input(label="Warning value.", step=1)
    with col8:
        st.number_input(label="Alert value.", step=1)
    with col9:
        st.number_input(label="Hysteresis value.", step=1)


    col10, col11, col12 = st.columns([1.3,1.5,3])
    with col10:
        if st.button(label="Write to config."):
            pass
    with col11:
        if st.button(label="Load default config."):
            pass

# TODO make layout prettier
# TODO add value parameter based on config to number input
# TODO read config on every loop in data_collector