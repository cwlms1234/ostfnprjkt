import streamlit as st
import pandas as pd
from datetime import datetime, time
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
    end_date = datetime.combine(end_date, time.max)

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
# TODO make layout prettier
