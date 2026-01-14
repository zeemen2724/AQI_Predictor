import os
from datetime import datetime, timedelta
import hopsworks
import pandas as pd

from src.data_ingestion.fetch_openmeteo import fetch_openmeteo_data
from src.data_ingestion.fetch_aqicn import fetch_aqicn_live
from src.features.build_features import build_features
from src.feature_store.push_to_hopsworks import (
    push_features,
    get_last_ingested_timestamp
)

def main():
    print("🔄 Starting AQI pipeline...")

    project = hopsworks.login(
        api_key_value=os.getenv("HOPSWORKS_API_KEY"),
        project=os.getenv("HOPSWORKS_PROJECT")
    )
    fs = project.get_feature_store()

    last_ts = get_last_ingested_timestamp(fs)

    # ─────────────────────────────
    # BOOTSTRAP → OPEN-METEO
    # ─────────────────────────────
    if last_ts is None:
        start_date = (datetime.utcnow() - timedelta(days=90)).strftime("%Y-%m-%d")
        end_date = datetime.utcnow().strftime("%Y-%m-%d")

        print(f"🆕 Bootstrap run → Open-Meteo {start_date} → {end_date}")

        df_raw = fetch_openmeteo_data(start_date, end_date)

    # ─────────────────────────────
    # INCREMENTAL → AQICN
    # ─────────────────────────────
    else:
        print("⚡ Incremental run → AQICN")

        df_new = fetch_aqicn_live()

        if df_new.empty:
            print("🟡 No AQICN data.")
            return

        if df_new["timestamp"].iloc[0] <= last_ts:
            print("🟡 AQICN data already ingested.")
            return

        # 🔥 Pull last 48 hours for lag continuity
        fg = fs.get_feature_group("karachi_air_quality", version=2)
        df_hist = fg.read(
            start_time=last_ts - timedelta(hours=48),
            end_time=last_ts
        )

        df_raw = pd.concat([df_hist, df_new], ignore_index=True)

    # ─────────────────────────────
    # FEATURE ENGINEERING
    # ─────────────────────────────
    print("🧠 Building features...")
    df_features = build_features(df_raw)

    # Keep ONLY the newest row
    df_features = df_features.sort_values("timestamp").tail(1)

    if df_features.empty:
        print("🟡 No features to push.")
        return

    # ─────────────────────────────
    # PUSH
    # ─────────────────────────────
    push_features(df_features)

    print("✅ AQI pipeline completed")

if __name__ == "__main__":
    main()
