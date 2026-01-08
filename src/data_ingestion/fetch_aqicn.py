import os
import requests

API_KEY = os.getenv("AQICN_API_KEY")

def fetch_aqicn_live(city="karachi"):
    url = f"https://api.waqi.info/feed/{city}/?token={API_KEY}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
