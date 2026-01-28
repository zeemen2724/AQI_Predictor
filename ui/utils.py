import os
import joblib
import pandas as pd
import hopsworks
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
os.environ["HOPSWORKS_DISABLE_MODEL_SERVING"] = "1"

@st.cache_data
def load_latest_data():
    return pd.read_parquet("../artifacts/latest_features.parquet")

@st.cache_resource
def load_model():
    """
    Load latest model from Hopsworks Model Registry.
    Falls back to local model if registry unavailable.
    """
    try:
        project = hopsworks.login(
            api_key_value=os.getenv("HOPSWORKS_API_KEY"),
            project=os.getenv("HOPSWORKS_PROJECT_NAME"),
        )

        mr = project.get_model_registry()

        # 🔥 Fetch all versions and pick latest
        models = mr.get_models(name="aqi_predictor")
        if len(models) == 0:
            raise RuntimeError("No models found in registry")

        latest_model = max(models, key=lambda m: m.version)

        model_dir = latest_model.download()
        model_path = os.path.join(model_dir, "model.joblib")

        print(f"✅ Model loaded from Hopsworks registry v{latest_model.version}")
        return joblib.load(model_path)

    except Exception as e:
        print(f"⚠️ Registry load failed, using local model. Reason: {e}")
        return joblib.load("../artifacts/model.joblib")



def get_latest_aqi(df):
    latest = df.iloc[-1]
    return latest["timestamp"], latest["aqi"]

def aqi_category(aqi):
    if aqi <= 50:
        return "Good 😌", "green"
    elif aqi <= 100:
        return "Moderate 🙂", "yellow"
    elif aqi <= 150:
        return "Unhealthy (Sensitive) 😐", "orange"
    elif aqi <= 200:
        return "Unhealthy 😷", "red"
    elif aqi <= 300:
        return "Very Unhealthy 🤢", "purple"
    else:
        return "Hazardous ☠️", "maroon"

import json

def load_metrics():
    with open("../artifacts/metrics.json", "r") as f:
        return json.load(f)

