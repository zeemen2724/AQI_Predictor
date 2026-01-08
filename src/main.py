from src.data_ingestion.fetch_openmeteo import fetch_openmeteo_data
from src.features.build_features import build_features
from src.feature_store.push_to_hopsworks import push_features

if __name__ == "__main__":
    print("Fetching historical data...")
    df_raw = fetch_openmeteo_data(
        start_date="2024-10-01",
        end_date="2025-01-01"
    )

    print("Building features...")
    df_features = build_features(df_raw)

    print("Pushing to Hopsworks...")
    push_features(df_features)

    print("Pipeline completed successfully 🚀")
