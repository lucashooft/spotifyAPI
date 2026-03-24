from dotenv import load_dotenv
import os
import requests
import time
import json

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
TOKENS_FILE = "tokens.json"

def save_tokens(access_token, refresh_token, expires_at):
    with open(TOKENS_FILE, "w") as f:
        json.dump({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at
        }, f)

def load_tokens():
    with open(TOKENS_FILE, "r") as f:
        return json.load(f)

def valid_token():
    tokens = load_tokens()

    if time.time() < tokens["expires_at"]:
        print("Token still valid")
        return tokens["access_token"]

    print("Token expired, refresh...")
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"]
        }
    )
    data = response.json()
    save_tokens(data["access_token"], data["refresh_token"], data["expires_at"])
    print("Token refreshed and saved")
    return data["access_token"]

def get_activities(token, pagina=1, per_pagina=30):
    response = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers={"Authorization": f"Bearer {token}"},
        params={"per_page": per_pagina, "page": pagina}
    )
    return response.json()

if not os.path.exists(TOKENS_FILE):
    save_tokens(
        os.getenv("STRAVA_ACCESS_TOKEN"),
        os.getenv("STRAVA_REFRESH_TOKEN"),
        0
    )
    print("tokens.json created from .env")


token = valid_token()

activities = get_activities(token)

print("\nACTIVITIES")
print("___________________________________________")

for activity in activities:
    print(f"\nName: {activity['name']}")
    print(f"Type: {activity['type']}")
    print(f"Distance: {round(activity['distance'] / 1000, 2)} km")
    seconds = activity['elapsed_time']
    hours = seconds //60 //60
    seconds = activity['elapsed_time']
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        print(f"Duration: {hours}h {minutes}m")
    else:
        print(f"Duration: {minutes}m")
    print(f"Date: {activity['start_date_local']}")
    print("___________________________________________")
