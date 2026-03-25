import streamlit as st
import pandas as pd
from supabase_client import select

st.title("Strava Dashboard")

activities = select("activities")
df = pd.DataFrame(activities)

df['start_date_local'] = pd.to_datetime(df['start_date_local'])
df['month'] = df['start_date_local'].dt.to_period('M').astype(str)

df['distance_km'] = df['distance'] / 1000

col1, col2 = st.columns(2)
col1.metric("Total activities", len(df))
col2.metric("Total distance", f"{df['distance_km'].sum():.0f} km")

st.subheader("Distance per month")
month_data = df.groupby('month')['distance_km'].sum().reset_index()
st.bar_chart(month_data.set_index('month'))

st.subheader("Recent activities")
recent = df[['start_date_local', 'name', 'distance_km']].sort_values('start_date_local', ascending=False).head(10)
recent.columns = ['Date', 'Name', 'Distance (km)']
recent['Distance (km)'] = recent['Distance (km)'].round(2)
st.dataframe(recent)