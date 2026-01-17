
import os
os.environ["HOPSWORKS_DISABLE_MODEL_SERVING"] = "1"

from datetime import datetime, timedelta
import hopsworks
import pandas as pd

from src.data_ingestion.fetch_openmeteo import fetch_openmeteo_data
from src.data_ingestion.fetch_aqicn import fetch_aqicn_live
from src.features.build_features import build_features
from src.feature_store.push_to_hopsworks import push_features


# 🔥 IMPORTANT: bootstrap must be MANUAL
BOOTSTRAP = False   # set True ONLY once, then switch back to False


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
    # BOOTSTRAP MODE (ONE TIME ONLY)
    # ─────────────────────────────
    if BOOTSTRAP:
        start_date = (datetime.utcnow() - timedelta(days=90)).strftime("%Y-%m-%d")
        end_date = datetime.utcnow().strftime("%Y-%m-%d")

        print(f"🆕 Bootstrap → Open-Meteo {start_date} → {end_date}")
        df_raw = fetch_openmeteo_data(start_date, end_date)

    # ─────────────────────────────
    # INCREMENTAL MODE (HOURLY)
    # ─────────────────────────────
    else:
        print("⚡ Incremental → AQICN")

        df_all = fg.read()

        if df_all.empty:
            print("🟡 Feature group empty. Run BOOTSTRAP once.")
            return
        
        df_latest = (
            df_all
            .sort_values("timestamp")
            .tail(1)
            .reset_index(drop=True)
        )



        if df_latest.empty:
            print("🟡 Online store empty. Run BOOTSTRAP once.")
            return

        last_event_id = df_latest["event_id"].iloc[0]
        last_ts = df_latest["timestamp"].iloc[0]

        df_new = fetch_aqicn_live()

        if df_new.empty:
            print("🟡 No AQICN data.")
            return

        new_event_id = df_new["event_id"].iloc[0]

        if new_event_id <= last_event_id:
            print("🟡 AQICN hour already ingested.")
            return

        # pull history for lag features
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

    # push ONLY newest hour
    df_features = df_features.sort_values("event_id").tail(1)

    if df_features.empty:
        print("🟡 No features to push.")
        return

    push_features(fg, df_features)

    print("✅ AQI pipeline completed")


if __name__ == "__main__":
    main()
