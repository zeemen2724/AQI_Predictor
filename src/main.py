import os
from datetime import datetime, timedelta
import hopsworks
import pandas as pd

from src.data_ingestion.fetch_openmeteo import fetch_openmeteo_data
from src.data_ingestion.fetch_aqicn import fetch_aqicn_live
from src.features.build_features import build_features
from src.feature_store.push_to_hopsworks import push_features


def main():
    print("🔄 Starting AQI pipeline...")

    project = hopsworks.login(
        api_key_value=os.getenv("HOPSWORKS_API_KEY"),
        project=os.getenv("HOPSWORKS_PROJECT_NAME")
    )
    fs = project.get_feature_store()

    fg = fs.get_feature_group("karachi_air_quality", version=2)

    # ─────────────────────────────
    # CHECK IF FEATURE GROUP EMPTY
    # ─────────────────────────────
    try:
        df_latest = fg.read(
            select=["event_id", "timestamp"],
            limit=1,
            sort_by="event_id",
            ascending=False
        )
    except Exception:
        df_latest = pd.DataFrame()

    # ─────────────────────────────
    # BOOTSTRAP → OPEN-METEO
    # ─────────────────────────────
    if df_latest.empty:
        start_date = (datetime.utcnow() - timedelta(days=90)).strftime("%Y-%m-%d")
        end_date = datetime.utcnow().strftime("%Y-%m-%d")

        print(f"🆕 Bootstrap → Open-Meteo {start_date} → {end_date}")

        df_raw = fetch_openmeteo_data(start_date, end_date)

    # ─────────────────────────────
    # INCREMENTAL → AQICN
    # ─────────────────────────────
    else:
        print("⚡ Incremental → AQICN")

        last_event_id = df_latest["event_id"].iloc[0]

        df_new = fetch_aqicn_live()

        if df_new.empty:
            print("🟡 No AQICN data.")
            return

        new_event_id = df_new["event_id"].iloc[0]

        if new_event_id <= last_event_id:
            print("🟡 AQICN hour already ingested.")
            return

        # 🔥 Pull last 48h for lag continuity
        last_ts = df_latest["timestamp"].iloc[0]

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

    # Keep ONLY the newest hour
    df_features = df_features.sort_values("event_id").tail(1)

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
