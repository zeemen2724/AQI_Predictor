import os
from datetime import datetime, timedelta
import hopsworks

from src.data_ingestion.fetch_openmeteo import fetch_openmeteo_data
from src.features.build_features import build_features
from src.feature_store.push_to_hopsworks import push_features, get_last_ingested_timestamp


def main():
    print("🔄 Starting AQI pipeline...")

    # Login once
    project = hopsworks.login(
        api_key_value=os.getenv("HOPSWORKS_API_KEY"),
        project=os.getenv("HOPSWORKS_PROJECT")
    )
    fs = project.get_feature_store()

    # Get last ingested timestamp
    last_ts = get_last_ingested_timestamp(fs)

    if last_ts is None:
        # First ever run (bootstrap)
        start_date = (datetime.utcnow() - timedelta(days=90)).strftime("%Y-%m-%d")
        print(f"🆕 First run → fetching last 90 days from {start_date}")
    else:
        # Incremental run
        start_date = last_ts.strftime("%Y-%m-%d")
        print(f"📈 Incremental run → fetching data from {start_date}")

    # Fetch latest data
    df_raw = fetch_openmeteo_data(start_date=start_date)

    if df_raw.empty:
        print("🟡 No new data available. Exiting cleanly.")
        return

    print("🧠 Building features...")
    df_features = build_features(df_raw)

    print("📦 Pushing to Hopsworks...")
    push_features(df_features)

    print("✅ Pipeline completed successfully")


if __name__ == "__main__":
    main()
