from dotenv import load_dotenv
import os
import requests

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")

CODE = "7fe22a584043b78a5e264e6235d80e892b71d349"

response = requests.post(
	"https://www.strava.com/oauth/token",
	data={
		"client_id": CLIENT_ID,
		"client_secret": CLIENT_SECRET,
		"code": CODE,
		"grant_type": "authorization_code"
	}
)

data = response.json()

print("Access token: ", data.get("access_token"))
print("Refresh token: ", data.get("refresh_token"))
print("Expires at: ", data.get("expires_at"))
