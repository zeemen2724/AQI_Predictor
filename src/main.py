import os
from datetime import datetime, timedelta
import hopsworks

from src.data_ingestion.fetch_openmeteo import fetch_openmeteo_data
from src.data_ingestion.fetch_aqicn import fetch_aqicn_live
from src.features.build_features import build_features
from src.feature_store.push_to_hopsworks import (
    push_features,
    get_last_ingested_timestamp
)


def main():
    print("🔄 Starting AQI pipeline...")

    # Login ONCE
    project = hopsworks.login(
        api_key_value=os.getenv("HOPSWORKS_API_KEY"),
        project=os.getenv("HOPSWORKS_PROJECT")
    )
    fs = project.get_feature_store()

    # Check last ingested timestamp
    last_ts = get_last_ingested_timestamp(fs)

    # ─────────────────────────────────────────────
    # BOOTSTRAP RUN → Open-Meteo (historical)
    # ─────────────────────────────────────────────
    if last_ts is None:
        start_date = (datetime.utcnow() - timedelta(days=90)).strftime("%Y-%m-%d")
        end_date = datetime.utcnow().strftime("%Y-%m-%d")

        print(f"🆕 Bootstrap run → Open-Meteo from {start_date} to {end_date}")

        df_raw = fetch_openmeteo_data(
            start_date=start_date,
            end_date=end_date
        )

    # ─────────────────────────────────────────────
    # INCREMENTAL RUN → AQICN (live updates)
    # ─────────────────────────────────────────────
    else:
        print("⚡ Incremental run → AQICN live fetch")

        df_raw = fetch_aqicn_live()

        if df_raw.empty:
            print("🟡 AQICN returned no data. Exiting.")
            return

        if df_raw["timestamp"].iloc[0] <= last_ts:
            print("🟡 No new AQICN data since last ingestion.")
            return

    # ─────────────────────────────────────────────
    # FEATURE ENGINEERING
    # ─────────────────────────────────────────────
    print("🧠 Building features...")
    df_features = build_features(df_raw)

    if df_features.empty:
        print("🟡 No features generated. Exiting.")
        return

    # ─────────────────────────────────────────────
    # PUSH TO HOPSWORKS
    # ─────────────────────────────────────────────
    push_features(df_features)

    print("✅ AQI pipeline completed successfully")


if __name__ == "__main__":
    main()
