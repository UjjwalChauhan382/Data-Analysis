import streamlit as st
import pandas as pd
import numpy as np
# !pip install pydeck
import pydeck as pdk
import plotly.express as px

DATA_URL = ("Motor_Vehicle_Collisions_Crashes.csv")


st.title("Motor Vehicle Collisions in New York City (NYC  🗽🚗💥)")
st.markdown("This Web Application is a Streamlit dashboard that can be used to analyze motor vehicle collisions in NYC.")

@st.cache(persist=True)
def load_data(nrows):
	data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
	data.dropna(subset=['LATITUDE','LONGITUDE'], inplace=True)
	# lowercase = lambda x: str(x).lower()
	# data.rename(lowercase, axis='columns', inplace=True)
	data.rename(columns={'CRASH_DATE_CRASH_TIME': 'date/time'}, inplace=True)
	return data

data = load_data(100000)
original_data = data

st.header("Where are the most people injured in NYC?")
INJURED_PERSONS = st.slider("Number of Persons injured in vehicle collisions: ", 0, 19)
st.map(data.query("INJURED_PERSONS >= @INJURED_PERSONS")[['LATITUDE','LONGITUDE']].dropna(how="any"))

st.header("How many collisions occur during a given time of day?")
hour = st.slider("Hour to look at:", 0, 23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 23))
midpoint = (np.average(data['LATITUDE']), np.average(data['LONGITUDE']))

st.write(pdk.Deck(
	map_style="mapbox://styles/mapbox/light-v9",
	initial_view_state={
		"latitude": midpoint[0],
		"longitude": midpoint[1],
		"zoom": 11,
		"pitch": 50,
	},
	layers=[
		pdk.Layer(
		"HexagonLayer",
		data=data[['date/time','LATITUDE','LONGITUDE']],
		get_position=['LONGITUDE','LATITUDE'],
		radius=100,
		extruded=True, #for 2d to 3D
		pickable=True,
		elevation_scale=4,
		elevation_range=[0,1000],	
		),
	],
))

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour+1) % 24))

filtered = data[
	(data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour+1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute':range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute','crashes'],height=400)
st.write(fig)

st.header("Top 10 dangerous streets by affected type: ")
select = st.selectbox('Affected type of people', ['Pedestrians','Cyclists','Motorists'])

if select == 'Pedestrians':
	st.write(original_data.query("INJURED_PEDESTRIANS >= 1")[["ON_STREET_NAME","INJURED_PEDESTRIANS"]].sort_values(by=['INJURED_PEDESTRIANS'],ascending=False).dropna(how='any')[:10])
elif select == 'Cyclists':
	st.write(original_data.query("INJURED_CYCLISTS >= 1")[["ON_STREET_NAME","INJURED_CYCLISTS"]].sort_values(by=['INJURED_CYCLISTS'],ascending=False).dropna(how='any')[:10])
elif select == 'Motorists':
	st.write(original_data.query("INJURED_MOTORISTS >= 1")[["ON_STREET_NAME","INJURED_MOTORISTS"]].sort_values(by=['INJURED_MOTORISTS'],ascending=False).dropna(how='any')[:10])


if st.checkbox("Show Raw Data", False):
	st.subheader('Raw Data')
	st.write(data)