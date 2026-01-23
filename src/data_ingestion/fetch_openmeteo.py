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

    # 🔑 Open-Meteo REQUIRES end_date if start_date exists
    if end_date is None:
        end_date = start_date

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        # ✅ MUST be comma-separated string
        "hourly": (
            "pm2_5,pm10,carbon_monoxide,"
            "nitrogen_dioxide,sulphur_dioxide,ozone"
        ),
        "start_date": start_date,
        "end_date": end_date,
        "timezone": "UTC"
    }

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

    # ✅ Correct timestamp
    df["timestamp"] = pd.to_datetime(df["time"], utc=True)

    # ✅ Hourly event_id
    df["event_id"] = df["timestamp"].dt.strftime("%Y%m%d%H")

    # cleanup
    df.drop(columns=["time"], inplace=True)

    return df
