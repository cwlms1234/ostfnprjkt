import pandas as pd
import plotly.express as px


def create_heatmap_plot(df: pd.DataFrame, cfg: dict):
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
