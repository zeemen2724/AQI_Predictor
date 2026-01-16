import os
import requests
import pandas as pd

API_KEY = os.getenv("AQICN_API_KEY")


def fetch_aqicn_live(city="karachi"):
    url = f"https://api.waqi.info/feed/{city}/?token={API_KEY}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    if data.get("status") != "ok":
        return pd.DataFrame()

    d = data["data"]

    timestamp = pd.to_datetime(d["time"]["iso"], utc=True)

    row = {
        "timestamp": timestamp,
        "event_id": timestamp.strftime("%Y%m%d%H"),  # 🔑 HOURLY DEDUP KEY
        "pm2_5": d.get("iaqi", {}).get("pm25", {}).get("v"),
        "pm10": d.get("iaqi", {}).get("pm10", {}).get("v"),
        "carbon_monoxide": d.get("iaqi", {}).get("co", {}).get("v"),
        "nitrogen_dioxide": d.get("iaqi", {}).get("no2", {}).get("v"),
        "sulphur_dioxide": d.get("iaqi", {}).get("so2", {}).get("v"),
        "ozone": d.get("iaqi", {}).get("o3", {}).get("v"),
    }

    return pd.DataFrame([row])
