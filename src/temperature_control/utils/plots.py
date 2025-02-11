import pandas as pd
import plotly.express as px


def create_heatmap_plot(df: pd.DataFrame, cfg: dict): # TODO fix timestamp error
    col_names = cfg["db"]["column_names"]

    # Ensure 'timestamp_col' is in datetime format
    df[col_names["timestamp"]] = pd.to_datetime(df[col_names["timestamp"]])

    # Extract weekday
    # df["weekday"] = df[col_names["timestamp"]].dt.day_name()
    df["weekday"] = df[col_names["timestamp"]].dt.strftime("%a")

    # Round the time to the nearest 30 minute interval
    df["time"] = df[col_names["timestamp"]].dt.floor("30min").dt.strftime("%H:%M")

    # Filter times between 07:00 and 20:00
    time_filter = (df["time"] >= "07:00") & (df["time"] <= "20:00")
    df = df[time_filter]

    # Fix weekday ordering
    weekdays_order = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun",
    ]
    df["weekday"] = pd.Categorical(
        df["weekday"],
        categories=weekdays_order,
        ordered=True,
    )

    # Ensure time is sorted in chronological order
    df["time"] = pd.to_datetime(df["time"], format="%H:%M").dt.strftime("%H:%M")

    # Pivot data to create a matrix for the heatmap
    heatmap_data = df.pivot_table(
        index="time", columns="weekday", values=col_names["temperature"], aggfunc="mean"
    )

    # Plot the heatmap
    fig = px.imshow(
        heatmap_data,
        labels={"x": "Weekday", "y": "Time", "color": col_names["temperature"]},
        color_continuous_scale="bluered",  # Adjust color scale if needed
        title="Temperature Heatmap by Weekday and Time",
        aspect="auto",
    )

    fig.update_xaxes(side="top")
    fig.update_layout(
        autosize=True,
        width=None,
        height=1000,
        margin=dict(
            b=100,
            t=150,
            l=50,
            r=50,
        ),
    )

    return fig

def create_pump_diagram(df: pd.DataFrame, cfg: dict):
    activity_sum = df[cfg["db"]["column_names"]["update_interval"]].sum()
    pump_activity_sum = df[cfg["db"]["column_names"]["pump_activation"]].sum()
    uptime_ratio = pump_activity_sum/activity_sum

    # Create a DataFrame for the pie chart
    pie_data = pd.DataFrame({
    "Category": ["inactive", "active"],
    "Value": [uptime_ratio * 100, 100 - (uptime_ratio * 100)]  # Convert ratio to percentage
    })

    # Create the pie chart
    return px.pie(pie_data, names="Category", values="Value", title=f"Pump Activation Ratio: {uptime_ratio*100:.2f}%")

# def create_temperature_distribution_chart(df: pd.DataFrame, cfg:dict):
#     # Create temperature bins with a step of 1°C
#     df['temp_bin'] = pd.cut(df[cfg["db"]["column_names"]["temperature"]], bins=range(int(df[cfg["db"]["column_names"]["temperature"]].min()), int(df[cfg["db"]["column_names"]["temperature"]].max()) + 2), right=False)
#     # Count the values in each bin
#     bin_counts = df['temp_bin'].value_counts().reset_index().astype(str)

#     bin_counts.columns = ['Temperature Bin', 'Count']
    

#     # Create a bar chart to show the distribution
#     return px.bar(bin_counts, x='Temperature Bin', y='Count', title='Temperature Distribution in 1°C Steps')

def create_temperature_distribution_chart(df: pd.DataFrame, cfg: dict):
    df["Temp Interval"] = df[cfg["db"]["column_names"]["temperature"]].round().astype(int)
    fig = px.histogram(df, x="Temp Interval")
    fig.update_layout(bargap=0.2)
    return fig
