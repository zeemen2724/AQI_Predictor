import requests
import pandas as pd
from datetime import datetime, timezone


def fetch_aqicn_live():
    url = "https://api.waqi.info/feed/karachi/"
    token = "YOUR_AQICN_TOKEN"

    response = requests.get(url, params={"token": token}, timeout=10)
    data = response.json()

    if data.get("status") != "ok":
        print("⚠️ AQICN API status not OK")
        return pd.DataFrame()

    iaqi = data["data"].get("iaqi", {})
    time_info = data["data"].get("time", {})

    if "pm25" not in iaqi:
        print("⚠️ PM2.5 missing in AQICN")
        return pd.DataFrame()

    ts = datetime.fromisoformat(time_info["iso"]).astimezone(timezone.utc)

    row = {
        "event_id": int(ts.timestamp()),
        "timestamp": ts,
        "pm2_5": iaqi["pm25"]["v"]
    }

    print(f"📡 AQICN returned timestamp: {ts}")

    return pd.DataFrame([row])
