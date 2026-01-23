import os
os.environ["HOPSWORKS_DISABLE_MODEL_SERVING"] = "1"

from datetime import datetime, timedelta
import hopsworks
import pandas as pd
import time

from src.data_ingestion.fetch_openmeteo import fetch_openmeteo_data
from src.data_ingestion.fetch_aqicn import fetch_aqicn_live
from src.features.build_features import build_features
from src.feature_store.push_to_hopsworks import push_features


# ─────────────────────────────
# SAFE FEATURE STORE READ
# ─────────────────────────────
def safe_read(fg, retries=3, wait=10):
    for i in range(retries):
        try:
            print("📥 Reading feature store (full read)...")
            return fg.read(read_options={"use_hudi": False})
        except Exception as e:
            print(f"⚠️ Read failed ({i+1}/{retries}): {e}")
            time.sleep(wait)
    raise RuntimeError("❌ Feature Store read failed after retries")


# ⚠️ RUN TRUE ONLY ONCE
BOOTSTRAP = False


def main():
    print("🔄 Starting AQI pipeline...")

    project = hopsworks.login(
        api_key_value=os.getenv("HOPSWORKS_API_KEY"),
        project=os.getenv("HOPSWORKS_PROJECT_NAME"),
    )
    fs = project.get_feature_store()

    fg = fs.get_feature_group(
        name="karachi_air_quality",
        version=2
    )

    # ─────────────────────────────
    # BOOTSTRAP (ONE TIME ONLY)
    # ─────────────────────────────
    if BOOTSTRAP:
        start_date = (datetime.utcnow() - timedelta(days=90)).strftime("%Y-%m-%d")
        end_date = datetime.utcnow().strftime("%Y-%m-%d")

        print(f"🆕 Bootstrapping data {start_date} → {end_date}")
        df_raw = fetch_openmeteo_data(start_date, end_date)

    # ─────────────────────────────
    # INCREMENTAL MODE
    # ─────────────────────────────
    else:
        df_hist = safe_read(fg)

        if df_hist.empty:
            print("🟡 Feature store empty. Run BOOTSTRAP once.")
            return

        df_hist = df_hist.sort_values("timestamp")
        last_ts = df_hist["timestamp"].iloc[-1]
        last_event_id = df_hist["event_id"].iloc[-1]

        print(f"⏱️ Last ingested timestamp: {last_ts}")

        df_new = fetch_aqicn_live()

        if df_new.empty:
            print("🟡 No AQICN data.")
            return

        new_event_id = df_new["event_id"].iloc[0]
        new_ts = df_new["timestamp"].iloc[0]

        print(f"🌍 AQICN timestamp: {new_ts}")

        if new_event_id <= last_event_id:
            print("🟡 AQICN not updated yet. Skipping ingestion.")
            return

        df_context = df_hist[
            df_hist["timestamp"] > last_ts - timedelta(hours=48)
        ]

        df_raw = pd.concat([df_context, df_new], ignore_index=True)

    # ─────────────────────────────
    # FEATURE ENGINEERING
    # ─────────────────────────────
    print("🧠 Building features...")
    df_features = build_features(df_raw)

    df_features = df_features.sort_values("event_id").tail(1)

    if df_features.empty:
        print("🟡 No features to push.")
        return

    push_features(fg, df_features)

    print("✅ AQI pipeline completed successfully")


if __name__ == "__main__":
    main()
