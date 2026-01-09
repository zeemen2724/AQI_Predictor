import os
import hopsworks
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def push_features(df: pd.DataFrame):
    project = hopsworks.login(
        project=os.getenv("HOPSWORKS_PROJECT_NAME"),
        api_key_value=os.getenv("HOPSWORKS_API_KEY")
    )

    fs = project.get_feature_store()

    fg = fs.get_or_create_feature_group(
        name="karachi_air_quality",
        version=1,
        description="Hourly air quality data for Karachi",
        primary_key=["timestamp"],
        online_enabled=True
    )

    fg.insert(df)

    print("✅ Data pushed to Hopsworks Feature Store")


