import pandas as pd


def compute_aqi_pm25(pm25):
    # EPA standard AQI breakpoints for PM2.5 (24-hr, but works for hourly too)
    breakpoints = [
        (0,    12.0,   0,   50),
        (12.1, 35.4,  51,  100),
        (35.5, 55.4, 101,  150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]
    for lo, hi, aqi_lo, aqi_hi in breakpoints:
        if lo <= pm25 <= hi:
            return aqi_lo + (pm25 - lo) * (aqi_hi - aqi_lo) / (hi - lo)
    # If somehow above 500.4, scale linearly beyond 500
    return 500 + (pm25 - 500.4)

def build_features(df):
    df = df.copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    # ✅ REQUIRED PRIMARY KEY
    df["event_id"] = df["timestamp"].astype("int64") // 10**9

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

