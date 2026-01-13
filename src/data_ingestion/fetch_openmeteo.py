import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.utils.config import LATITUDE, LONGITUDE, OPEN_METEO_URL


def fetch_openmeteo_data(start_date, end_date=None):
    session = requests.Session()

    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    session.mount("https://", HTTPAdapter(max_retries=retries))

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": [
            "pm2_5",
            "pm10",
            "carbon_monoxide",
            "nitrogen_dioxide",
            "sulphur_dioxide",
            "ozone"
        ],
        "start_date": start_date
    }

    # 👇 ONLY include end_date if explicitly provided
    if end_date is not None:
        params["end_date"] = end_date

    response = session.get(
        OPEN_METEO_URL,
        params=params,
        timeout=30
    )
    response.raise_for_status()

    data = response.json()

    if "hourly" not in data:
        return pd.DataFrame()

    df = pd.DataFrame(data["hourly"])
    df["timestamp"] = pd.to_datetime(df["time"])
    df.drop(columns=["time"], inplace=True)

    return df
