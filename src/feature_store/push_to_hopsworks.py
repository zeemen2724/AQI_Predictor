import hopsworks
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def get_last_ingested_timestamp(fs):
    """
    Fetch the most recent timestamp from the feature group
    """
    try:
        fg = fs.get_feature_group(
            name="karachi_air_quality",
            version=2   # ✅ MUST MATCH WRITE VERSION
        )
        df_last = fg.read(
            select=["timestamp"],
            limit=1,
            sort_by="timestamp",
            ascending=False
        )
        return df_last["timestamp"].iloc[0]
    except Exception:
        return None


def push_features(df: pd.DataFrame):
    """
    Push engineered features to Hopsworks Feature Store
    """
    print("Pushing to Hopsworks...")

    project = hopsworks.login(
        api_key_value=os.getenv("HOPSWORKS_API_KEY"),
        project=os.getenv("HOPSWORKS_PROJECT")
    )
    fs = project.get_feature_store()

    df = df.copy()

    fg = fs.get_or_create_feature_group(
        name="karachi_air_quality",
        version=2,
        primary_key=["event_id"],
        event_time="timestamp",
        online_enabled=False,
        description="Karachi AQI features with pollutants and time-based features"
    )

    fg.insert(df)
    print(f"✅ Pushed {len(df)} records to Hopsworks Feature Store")
