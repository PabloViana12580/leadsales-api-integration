import json
import os
from pathlib import Path
import time
from urllib.parse import urljoin

import environ
import requests
from requests import RequestException

from .models import Stage

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize Environ
env = environ.Env()

# Load the .env file located at BASE_DIR/.env
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

ls_sales_endpoint = "https://public.leadsales.services/v1/funnels"
ls_auth_endpoint = "https://public.leadsales.services/v1/auth/token"

REQUEST_TIMEOUT_SECONDS = 30
MAX_REQUEST_ATTEMPTS = 6
INITIAL_RETRY_DELAY_SECONDS = 2
MAX_RETRY_DELAY_SECONDS = 60


class LeadSalesAPIError(Exception):
    """Raised when LeadSales cannot return a complete response."""


def _retry_delay(response, attempt):
    retry_after = response.headers.get("Retry-After") if response is not None else None
    if retry_after:
        try:
            return min(float(retry_after), MAX_RETRY_DELAY_SECONDS)
        except ValueError:
            pass

    return min(
        INITIAL_RETRY_DELAY_SECONDS * (2 ** (attempt - 1)),
        MAX_RETRY_DELAY_SECONDS,
    )


def _request_with_retries(method, url, **kwargs):
    """Call LeadSales with retry/backoff so 429s do not truncate lead downloads."""
    kwargs.setdefault("timeout", REQUEST_TIMEOUT_SECONDS)

    last_error = None
    for attempt in range(1, MAX_REQUEST_ATTEMPTS + 1):
        response = None
        try:
            response = requests.request(method, url, **kwargs)
            print("STATUS:", response.status_code)

            if response.status_code == 429:
                delay = _retry_delay(response, attempt)
                print(
                    f"LeadSales rate limit hit for {url}. "
                    f"Retrying in {delay} seconds "
                    f"({attempt}/{MAX_REQUEST_ATTEMPTS})."
                )
                if attempt < MAX_REQUEST_ATTEMPTS:
                    time.sleep(delay)
                    continue

            response.raise_for_status()
            return response
        except RequestException as exc:
            last_error = exc
            if attempt >= MAX_REQUEST_ATTEMPTS:
                break
            delay = _retry_delay(response, attempt)
            print(
                f"LeadSales request failed for {url}: {exc}. "
                f"Retrying in {delay} seconds "
                f"({attempt}/{MAX_REQUEST_ATTEMPTS})."
            )
            time.sleep(delay)

    raise LeadSalesAPIError(
        f"LeadSales request failed after {MAX_REQUEST_ATTEMPTS} attempts: {last_error}"
    )


def _decode_json_response(response):
    try:
        return response.json()
    except json.JSONDecodeError as exc:
        print("Failed to decode JSON. Raw response:", response.text)
        raise LeadSalesAPIError("LeadSales returned a non-JSON response.") from exc


def get_auth_token():
    payload = {
        "workspace_id": env("WORKSPACE_ID"),
        "publishable_key": env("PUBLISHABLE_KEY"),
        "secret_key": env("SECRET_KEY"),
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://leadsales.io",
        "Referer": "https://leadsales.io/",
    }

    response = _request_with_retries("post", ls_auth_endpoint, json=payload, headers=headers)
    data = _decode_json_response(response)

    access_token = data.get("access_token")
    if not access_token:
        print("❌ Missing access_token. Full response:")
        print(json.dumps(data, indent=2))
        raise ValueError("access_token missing from LeadSales response")

    headers["Authorization"] = f"Bearer {access_token}"
    return headers


def get_funnels():
    headers_auth = get_auth_token()
    funnels_data = _request_with_retries("get", ls_sales_endpoint, headers=headers_auth)
    return _decode_json_response(funnels_data).get("data", [])


def iter_leads_for_stage(stageid):
    stage_instance = Stage.objects.get(stageid=stageid)
    headers_auth = get_auth_token()
    print(
        f"⏳ Fetching leads for stage: {stage_instance.stagename} ({stage_instance.leads_count} leads expected)"
    )

    fetched_count = 0
    url = f"https://public.leadsales.services/v1/leads/{stage_instance.stageid}"

    while url:
        response = _request_with_retries("get", url, headers=headers_auth)
        data = _decode_json_response(response)

        page_leads = data.get("data", [])
        for lead in page_leads:
            fetched_count += 1
            yield lead

        next_page_url = data.get("pagination", {}).get("next_page_url")
        url = urljoin("https://public.leadsales.services", next_page_url) if next_page_url else None

        print(
            f"✅ Collected {fetched_count} leads from stage '{stage_instance.stagename}'."
        )

    if fetched_count < stage_instance.leads_count:
        print(
            f"⚠️ LeadSales returned {fetched_count} leads for stage "
            f"'{stage_instance.stagename}', but {stage_instance.leads_count} were expected."
        )


def get_leads_for_stage(stageid):
    return list(iter_leads_for_stage(stageid))
