# ===========================
# SINGLE SOURCE OF TRUTH
# These constants are imported by train_models.py and utils.py
# so all three files stay in sync.
# ===========================
LAGS = [1, 24, 48]
TIME_FEATURES = ["hour", "day", "month", "weekday"]
TARGET = "aqi"
FEATURES = [f"{TARGET}_lag_{lag}" for lag in LAGS] + TIME_FEATURES
# Result: ["aqi_lag_1", "aqi_lag_24", "aqi_lag_48", "hour", "day", "month", "weekday"]


def create_lag_features(df):
    """
    Creates lag features and time features on the historical DataFrame.
    Call this ONCE before training or before you hand data to the forecast loop.
    """
    df = df.sort_values("timestamp").copy()

    # Lag features — shift AQI by 1h, 24h, 48h
    for lag in LAGS:
        df[f"{TARGET}_lag_{lag}"] = df[TARGET].shift(lag)

    # Time features
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.day
    df["month"] = df["timestamp"].dt.month
    df["weekday"] = df["timestamp"].dt.weekday  # <-- was missing before

    # Drop rows where any lag is NaN (the first 48 rows)
    df.dropna(subset=FEATURES, inplace=True)

    return df