from dotenv import load_dotenv
import os
import requests
import base64

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_access_token(client_id, client_secret):
	credentials = f"{client_id}:{client_secret}"
	encoded = base64.b64encode(credentials.encode()).decode()

	response = requests.post(
		"https://accounts.spotify.com/api/token",
		headers={
			"Authorization": f"Basic {encoded}",
			"Content-Type": "application/x-www-form-urlencoded"
		},
		data="grant_type=client_credentials"
	)

	print("Status code: ", response.status_code)
	print("Response: ", response.json())
	
	return response.json()["access_token"] 

def search_artist(token, name):
	response = requests.get(
		"https://api.spotify.com/v1/search",
		headers={"Authorization": f"Bearer {token}"},
	 	params={"q": name, "type": "artist", "limit": 1}
	)


	items = response.json()["artists"]["items"]
	return items[0] if items else None

def get_artist_details(token, artist_id):
	response = requests.get(
		f"https://api.spotify.com/v1/artists/{artist_id}",
		headers={"Authorization": f"Bearer {token}"}
	)
	return response.json()
	
def get_artist_albums(token, artist_id):
	response = requests.get(
		f"https://api.spotify.com/v1/artists/{artist_id}/albums",
		headers={"Authorization": f"Bearer {token}"}
	)
	return response.json()

token = get_access_token(CLIENT_ID, CLIENT_SECRET)
artist = search_artist(token, "Nirvana")
albums = get_artist_albums(token, artist["id"])

print(f"Artist: {artist['name']}\n")

counter = 0
for album in albums['items']:
	counter += 1
	print(f"Album #{counter}: {album['name']}")
