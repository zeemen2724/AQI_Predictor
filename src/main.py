import os
from tracemalloc import start
os.environ["HOPSWORKS_DISABLE_MODEL_SERVING"] = "1"

from datetime import datetime, timedelta
import hopsworks
import pandas as pd
import time
from dotenv import load_dotenv  # ← ADD THIS

# Load environment variables from .env file
load_dotenv()  # ← ADD THIS

from src.data_ingestion.fetch_openmeteo import fetch_openmeteo_data
from src.features.build_features import build_features
from src.feature_store.push_to_hopsworks import push_features


BOOTSTRAP = False  


def safe_read(fg, retries=3, wait=10):
    for i in range(retries):
        try:
            return fg.read()
        except Exception as e:
            print(f"⚠️ Read failed ({i+1}/{retries}): {e}")
            time.sleep(wait)
    raise RuntimeError("Feature store read failed")


def main():
    print("🔄 Starting Open-Meteo AQI pipeline...")

    project = hopsworks.login(
        api_key_value=os.getenv("HOPSWORKS_API_KEY"),
        project=os.getenv("HOPSWORKS_PROJECT_NAME"),
    )
    fs = project.get_feature_store()

    fg = fs.get_or_create_feature_group(
    name="karachi_air_quality",
    version=3,
    primary_key=["event_id"],
    event_time="timestamp",
    description="Karachi AQI hourly features from Open-Meteo",
    online_enabled=False
    )


    # ---------------------------
    # BOOTSTRAP
    # ---------------------------
    if BOOTSTRAP:
        start = (datetime.utcnow() - timedelta(days=90)).strftime("%Y-%m-%d")
        end = datetime.utcnow().strftime("%Y-%m-%d")

        print(f"🆕 Bootstrapping {start} → {end}")
        df_raw = fetch_openmeteo_data(start, end)

    # ---------------------------
    # INCREMENTAL
    # ---------------------------
    else:
        df_hist = safe_read(fg)
    
        if df_hist.empty:
            print("🟡 Feature store empty — run BOOTSTRAP")
            return
    
        last_ts = df_hist["timestamp"].max()
        print(f"⏱️ Last timestamp in FS: {last_ts}")
    
        start = last_ts.strftime("%Y-%m-%d")
        end = datetime.utcnow().strftime("%Y-%m-%d")
        
        df_raw = fetch_openmeteo_data(
            start_date=start,
            end_date=end
        )

    
        if df_raw.empty:
            print("🟡 No new Open-Meteo data")
            return


    # ---------------------------
    # FEATURES
    # ---------------------------

    last_ts = fg.read().max()["timestamp"]
    print(f"⏱️ Last timestamp in FS: {last_ts}")
    
    df_new = df_raw[df_raw["timestamp"] > last_ts]
    
    if df_new.empty:
        print("🟡 No new data to ingest. Skipping insert.")
        return

    df_features = build_features(df_raw)

    if df_features.empty:
        print("🟡 No features generated")
        return

    push_features(fg, df_features)
    print("✅ Pipeline finished successfully")


if __name__ == "__main__":
    main()