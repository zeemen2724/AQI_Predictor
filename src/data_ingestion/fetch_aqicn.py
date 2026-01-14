import os
import requests
import pandas as pd

API_KEY = os.getenv("AQICN_API_KEY")

def fetch_aqicn_live(city="karachi"):
    url = f"https://api.waqi.info/feed/{city}/?token={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    if data["status"] != "ok":
        return pd.DataFrame()

    d = data["data"]

    row = {
        "timestamp": pd.to_datetime(d["time"]["iso"]),
        "pm2_5": d["iaqi"].get("pm25", {}).get("v"),
        "pm10": d["iaqi"].get("pm10", {}).get("v"),
        "carbon_monoxide": d["iaqi"].get("co", {}).get("v"),
        "nitrogen_dioxide": d["iaqi"].get("no2", {}).get("v"),
        "sulphur_dioxide": d["iaqi"].get("so2", {}).get("v"),
        "ozone": d["iaqi"].get("o3", {}).get("v"),
    }

    return pd.DataFrame([row])
