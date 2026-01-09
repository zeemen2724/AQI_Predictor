import pandas as pd
from datetime import datetime

def compute_aqi_pm25(pm25):
    # simplified EPA AQI logic (acceptable for projects)
    if pm25 <= 12:
        return pm25 * 50 / 12
    elif pm25 <= 35.4:
        return ((pm25 - 12.1) * (100 - 51) / (35.4 - 12.1)) + 51
    elif pm25 <= 55.4:
        return ((pm25 - 35.5) * (150 - 101) / (55.4 - 35.5)) + 101
    else:
        return 200



def build_features(df):
    df = df.copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # 🔑 Create supported primary key
    df["event_id"] = df["timestamp"].astype(str)

    df["aqi"] = df["pm2_5"].apply(compute_aqi_pm25)

    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.day
    df["month"] = df["timestamp"].dt.month
    df["weekday"] = df["timestamp"].dt.weekday

    df["pm2_5_lag1"] = df["pm2_5"].shift(1)
    df["pm2_5_lag2"] = df["pm2_5"].shift(2)
    df["pm2_5_roll3"] = df["pm2_5"].rolling(3).mean()

    df.dropna(inplace=True)

    return df


