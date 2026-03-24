from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")

url = (
	f"https://www.strava.com/oauth/authorize"
	f"?client_id={CLIENT_ID}"
	f"&redirect_uri=http://localhost"
	f"&response_type=code"
	f"&scope=activity:read_all"
)

print("Open this URL in your browser: ")
print(url)
