
# TODO
# Download Button

import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

from measuring_assets.utils.measuring_utils import get_timestamp
import plotly.express as px

filepath = "~/git/ostfnprjkt/logs/11-2024.csv"

index = st.slider(label="Number of months to fetch", value = 1, min_value=1, max_value=12) # TODO build df according to specs
# TODO use @st.cache_data




df = pd.read_csv(filepath).sort_values(["Time"], ascending = False)
df["Time"] = pd.to_datetime(df["Time"]).dt.strftime("%H:%M:%S")
if st.checkbox("Show Raw Data"):
    st.dataframe(df, hide_index=True,)




#index = st.slider(label="Number of measurements to display", value = 20, max_value=200)
index = st.number_input(label="Number of measurements to display", value = 20)
df_chart = df.head(int(index))


#df.hvplot.points()
st.line_chart(df_chart, x = "Time", y = "Reading")

fig = px.scatter(df, x="Time", y="Reading")
event = st.plotly_chart(fig)