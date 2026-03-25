from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")

auth_url = (
    f"https://www.strava.com/oauth/authorize"
    f"?client_id={CLIENT_ID}"
    f"&redirect_uri=http://localhost"
    f"&response_type=code"
    f"&scope=activity:read_all,read_all,profile:write"
)

print()
print("Open this URL in your browser:")
print(auth_url)
print()
CODE = input("Paste the code from the redirect URL: ").strip()

response = requests.post(
    "https://www.strava.com/oauth/token",
    data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": CODE,
        "grant_type": "authorization_code",
        "redirect_uri": "http://localhost"
    }
)

data = response.json()
if "access_token" not in data:
    print("Error from Strava:", data)
else:
    with open("tokens.json", "w") as f:
        json.dump({
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_at": data["expires_at"]
        }, f)
    print("tokens.json opgeslagen!")
    print("Access token: ", data["access_token"])
    print("Refresh token: ", data["refresh_token"])
    print("Expires at: ", data["expires_at"])
