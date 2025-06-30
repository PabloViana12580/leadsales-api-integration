from datetime import datetime
import requests
import environ
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

#Initialize Environ
env = environ.Env()

# Load the .env file located at BASE_DIR/.env
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

ls_sales_endpoint = "https://public.leadsales.services/v1/funnels"
ls_auth_endopoit = "https://public.leadsales.services/v1/auth/token"

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

	response = requests.post(ls_auth_endopoit, json=payload, headers=headers).json()

	ACCESS_TOKEN = response["access_token"]

	headers["Authorization"] = f'Bearer {ACCESS_TOKEN}'
	
	return headers

def get_funnels():

	headers_auth = get_auth_token()
	funnels_data = requests.get(ls_sales_endpoint, headers=headers_auth).json().get("data", [])

	return funnels_data