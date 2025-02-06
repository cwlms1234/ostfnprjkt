from datetime import datetime, time

import pandas as pd
import plotly.express as px
import streamlit as st
from utils.general_utils import fetch_config, write_config
from utils.sql_utils import execute_sql_select, execute_sql_to_df

if "download_df" not in st.session_state:
    st.session_state["download_df"] = pd.DataFrame()

preview_df = False
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
col1, col2, col3 = st.columns(spec=3)

with col1:  # TODO adjust select to be more specific than *
    if st.button(label="Execute Search", use_container_width=True):
        query = f"""SELECT * 
                    FROM {table_name} 
                    WHERE {timestamp_col} >= '{start_date}' 
                    AND {timestamp_col} <= '{end_date}'"""
        st.session_state["download_df"] = execute_sql_to_df(db_name, query)
        st.success(f"Query fechted {len(st.session_state['download_df'])} lines!")

with col2:
    if st.button(label="Preview Data", use_container_width=True):
        preview_df = True

with col3:
    st.download_button(
        label="Download as CSV",  # TODO round filename if 1 day interval
        data=st.session_state["download_df"].to_csv().encode("utf-8"),
        file_name=f"{start_date}_{end_date}.csv",
        mime="text/csv",
        use_container_width=True,
    )

if preview_df:
    st.dataframe(data=st.session_state["download_df"], use_container_width=True)

st.markdown("#")


with st.expander(label="Adjust config:"):
    st.write("Measuring Parameters:")

    col4, col5, col6 = st.columns([1, 1, 1])
    with col4:
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

    with col5:
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

    with col6:
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

    col7, col8, col9 = st.columns([1, 1, 1])
    with col7:
        warning_limit = st.number_input(
            label="Warning value (°C)",
            step=1,
            value=st.session_state["config"]["temperature_thresholds"]["warning_limit"],
        )
        st.session_state["config"]["temperature_thresholds"]["warning_limit"] = (
            warning_limit
        )
    with col8:
        alert_limit = st.number_input(
            label="Alert value (°C)",
            step=1,
            value=st.session_state["config"]["temperature_thresholds"]["alert_limit"],
        )
        st.session_state["config"]["temperature_thresholds"]["alert_limit"] = (
            alert_limit
        )
    with col9:
        pass

    col10, col11 = st.columns(2)
    with col10:
        if st.button(label="Write to config", use_container_width=True):
            print(st.session_state["config"])
            write_config(st.session_state["config"])
    with col11:
        if st.button(label="Load default config", use_container_width=True):
            write_config(fetch_config("default_config.yaml"))

# TODO make layout prettier
# TODO add value parameter based on config to number input
# TODO read config on every loop in data_collector

if "download_df" in st.session_state and len(st.session_state["download_df"]) > 1:
    # st.session_state["download_df"][timestamp_col] = pd.to_datetime(st.session_state["download_df"][timestamp_col])

    # # Extract weekday and time
    # st.session_state["download_df"]['weekday'] = st.session_state["download_df"][timestamp_col].dt.day_name()
    # st.session_state["download_df"]['time'] = st.session_state["download_df"][timestamp_col].dt.strftime('%H:%M')

    # # Pivot data to create a matrix for the heatmap
    # heatmap_data = st.session_state["download_df"].pivot_table(index='time', columns='weekday', values=temp_col, aggfunc='mean')

    # # Plot the heatmap
    # fig = px.imshow(heatmap_data,
    #                 labels={'x': 'Weekday', 'y': 'Time', 'color': temp_col},
    #                 color_continuous_scale='Viridis',  # Adjust color scale if needed
    #                 title='Temperature Heatmap by Weekday and Time')

    # fig.update_xaxes(side='top')  # Optional: To put weekday labels on top
    # st.plotly_chart(figure_or_data=fig)

    # Ensure 'timestamp_col' is in datetime format
    st.session_state["download_df"][timestamp_col] = pd.to_datetime(
        st.session_state["download_df"][timestamp_col]
    )

    # Extract weekday and round time to the nearest 30 minutes
    st.session_state["download_df"]["weekday"] = st.session_state["download_df"][
        timestamp_col
    ].dt.day_name()

    # Round the time to the nearest 30 minutes
    st.session_state["download_df"]["time"] = (
        st.session_state["download_df"][timestamp_col]
        .dt.floor("30min")
        .dt.strftime("%H:%M")
    )

    # Filter times between 07:00 and 20:00
    time_filter = (st.session_state["download_df"]["time"] >= "07:00") & (
        st.session_state["download_df"]["time"] <= "20:00"
    )
    st.session_state["download_df"] = st.session_state["download_df"][time_filter]

    # Fix weekday ordering
    weekdays_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    st.session_state["download_df"]["weekday"] = pd.Categorical(
        st.session_state["download_df"]["weekday"],
        categories=weekdays_order,
        ordered=True,
    )

    # Ensure time is sorted in chronological order
    st.session_state["download_df"]["time"] = pd.to_datetime(
        st.session_state["download_df"]["time"], format="%H:%M"
    ).dt.strftime("%H:%M")

    # Pivot data to create a matrix for the heatmap
    heatmap_data = st.session_state["download_df"].pivot_table(
        index="time", columns="weekday", values=temp_col, aggfunc="mean"
    )

    # Plot the heatmap
    fig = px.imshow(
        heatmap_data,
        labels={"x": "Weekday", "y": "Time", "color": temp_col},
        color_continuous_scale="bluered",  # Adjust color scale if needed
        title="Temperature Heatmap by Weekday and Time",
        aspect="auto",
    )

    # Optional: Update x-axis to put weekday labels on top
    fig.update_xaxes(side="top")
    fig.update_layout(
        autosize=True,  # Let Plotly resize automatically
        width=None,  # Automatically adjusts based on container size
        height=1000,  # You can adjust the height if needed
        xaxis=dict(
            tickangle=45,  # Rotate the x-axis labels to 45 degrees to prevent overlap
            tickmode="array",  # Use an array mode to define ticks manually if needed
            tickvals=heatmap_data.columns,  # Ensure ticks match the columns (weekdays)
            ticktext=heatmap_data.columns,  # Show the weekday names properly
            ticklabelmode="instant",  # Show all labels at once without aggregation
            ticklen=10,  # Length of the ticks
        ),
        margin=dict(
            b=100,  # Increase bottom margin to give more space for x-axis labels
            t=50,  # Adjust top margin for the title
            l=50,  # Left margin
            r=50,  # Right margin
        ),
    )

    # Display the heatmap using Streamlit
    st.plotly_chart(figure_or_data=fig, use_container_width=True)
