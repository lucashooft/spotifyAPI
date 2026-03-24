from dotenv import load_dotenv
import os
import requests
import time

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")

def refresh_token():
	response = requests.post(
		"https://www.strava.com/oauth/token",
		data={
			"client_id": CLIENT_ID,
			"client_secret": CLIENT_SECRET,
			"grant_type": "refresh_token",
			"refresh_token": REFRESH_TOKEN
		}
	)
	data = response.json()
	return data["access_token"]

def get_activities(token, page=1, per_page=30):
	response = requests.get(
		"https://www.strava.com/api/v3/athlete/activities",
		headers={"Authorization": f"Bearer {token}"},
		params={"per_page": per_page, "page": page}
	)
	return response.json()

token = refresh_token()

activities = get_activities(token)

for activity in activities:
	print(f"Name: {activity['name']}")
	print(f"Type: {activity['type']}")
	print(f"Distance: {round(activity['distance'] / 1000, 2)} km")
	print(f"Date: {activity['start_date_local']}")
	print("________________________________________")
