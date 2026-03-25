from dotenv import load_dotenv
from supabase_client import insert, select, exists
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

def get_activities(token, per_page=30):
    all_activities = []
    page = 1
    while True:
        response = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers={"Authorization": f"Bearer {token}"},
            params={"per_page": per_page, "page": page}
        )
        data = response.json()

        if not data:
            break

        all_activities.extend(data)
        print(f"Page {page} fetched ({len(data)} activities)")
        page += 1    
    print(f"Total activities fetched: {len(all_activities)}")
    return all_activities

def get_activity_details(token, activity_id):
    response = requests.get(
        f"https://www.strava.com/api/v3/activities/{activity_id}",
        headers={"Authorization": f"Bearer {token}"},
        params={"include_all_efforts": True}
    )
    return response.json()

def star_segment(token, segment_id):
    response = requests.put(
        f"https://www.strava.com/api/v3/segments/{segment_id}/starred",
        headers={"Authorization": f"Bearer {token}"},
        json={"starred": True}
    )
    return response.json()

def get_starred_segments(token):
    response = requests.get(
        'https://www.strava.com/api/v3/segments/starred',
        headers={'Authorization': f'Bearer {token}'},
        params={'following': False}
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

starred_fragments = get_starred_segments(token)
starred_ids = {s['id'] for s in starred_fragments}

activities = get_activities(token)

print("\nACTIVITIES")
print("___________________________________________")

/*
for activity in activities:
    if (activity['type'] == "Ride" and not activity['trainer']):    
        details = get_activity_details(token, activity['id'])
        print(f"\nName: {details['name']}")
        print(f"Distance: {round(details['distance'] / 1000, 2)} km")

        seconds = details['elapsed_time']
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        if hours > 0:
            print(f"Duration: {hours}h {minutes}m")
        else:
            print(f"Duration: {minutes}m")

        print(f"Date: {details['start_date_local']}")

        segments = details.get('segment_efforts', [])
        if segments:
            print("Top segments:")

            for segment in segments:
                segment_id = segment['segment']['id']
                speed = segment['distance']/segment['elapsed_time']

                if (speed*3.6 >= 38):
                    if segment_id in starred_ids:
                        print(f"  {segment['name']} (already starred)")
                    else:
                        star_segment(token, segment['segment']['id'])
                        starred_ids.add(segment_id)
                        print(f"  {segment['name']}(starred)")
        print("___________________________________________")
*/
