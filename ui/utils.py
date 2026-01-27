import pandas as pd
import joblib

def load_latest_data():
    return pd.read_parquet("../artifacts/latest_features.parquet")

def load_model():
    return joblib.load("../artifacts/model.joblib")

def get_latest_aqi(df):
    latest = df.iloc[-1]
    return latest["timestamp"], latest["aqi"]
