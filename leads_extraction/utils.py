from datetime import datetime
import requests
import environ
import os
import json
from pathlib import Path
from .models import Stage

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

#Initialize Environ
env = environ.Env()

# Load the .env file located at BASE_DIR/.env
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

ls_sales_endpoint = "https://public.leadsales.services/v1/funnels"
ls_auth_endpoint = "https://public.leadsales.services/v1/auth/token"

def get_auth_token():

	payload = {
    	"workspace_id": env("WORKSPACE_ID"),
    	"publishable_key": env("PUBLISHABLE_KEY"),
    	"secret_key": env("SECRET_KEY")
	}

	headers = {
    	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    	"Content-Type": "application/json",
    	"Accept": "*/*",
    	"Origin": "https://leadsales.io",
    	"Referer": "https://leadsales.io/"
	}

	response = requests.post(ls_auth_endpoint, json=payload, headers=headers)

	try:
	    data = response.json()
	except json.JSONDecodeError:
	    print("Failed to decode JSON. Raw response:", response.text)
	    data = {}

	ACCESS_TOKEN = data["access_token"]

	headers["Authorization"] = f'Bearer {ACCESS_TOKEN}'
	
	return headers

def get_funnels():

	headers_auth = get_auth_token()
	funnels_data = requests.get(ls_sales_endpoint, headers=headers_auth)

	try:
	    data = funnels_data.json().get("data", [])
	except json.JSONDecodeError:
	    print("Failed to decode JSON. Raw response:", response.text)
	    data = {}

	return data

def get_leads_for_stage(stageid):
	stage_instance = Stage.objects.get(stageid=stageid)
	headers_auth = get_auth_token()
	print(f"⏳ Fetching leads for stage: {stage_instance.stagename} ({stage_instance.leads_count} leads expected)")

	leads = []
	url = f'https://public.leadsales.services/v1/leads/{stage_instance.stageid}'
	
	while url:
		response = requests.get(url, headers=headers_auth)

		print("STATUS:", response.status_code)
		print("TEXT:", response.text)  # see what you actually got back

		try:
		    data = response.json()
		except json.JSONDecodeError:
		    print("Failed to decode JSON. Raw response:", response.text)
		    data = {}
		
		if "data" in data:
			leads.extend(data["data"])

		url = data.get("pagination", {}).get("next_page_url")

		print(f"✅ Collected {len(leads)} leads from stage '{stage_instance.stagename}'.")

	return leads

