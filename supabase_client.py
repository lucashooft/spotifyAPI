from dotenv import load_dotenv
import os
import requests

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
	"apikey": SUPABASE_KEY,
	"Authorization": f"Bearer {SUPABASE_KEY}",
	"Content-Type": "application/json",
	"Prefer": "return=minimal"
}

def insert(table, data):
	response = requests.post(
		f"{SUPABASE_URL}/rest/v1/{table}",
		headers=HEADERS,
		json=data
	)
	return response.json()

def select(table):
	response = requests.get(
		f"{SUPABASE_URL}/rest/v1/{table}
		headeres=HEADERS
	)
	return response.json()

def exists(table, column, value):
	response = request.get(
		f"{SUPABASE_URL}/rest/v1/{table},
		headers=HEADERS,
		params={column: f"eq.{value}"}
	)
	return len(response.json()) > 0

