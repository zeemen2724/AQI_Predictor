import hopsworks
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

def push_features(df: pd.DataFrame):
    """
    Push engineered features to Hopsworks Feature Store
    """
    print("Pushing to Hopsworks...")
    
    # Login with API key
    api_key = os.getenv('HOPSWORKS_API_KEY')
    project_name = os.getenv('HOPSWORKS_PROJECT')
    
    project = hopsworks.login(
        api_key_value=api_key,
        project=project_name
    )
    fs = project.get_feature_store()
    
    # Create string-based primary key (Hopsworks online FG requirement)
    df = df.copy()
    df['event_id'] = df['timestamp'].astype(str)
    
    # Get or create feature group
    fg = fs.get_or_create_feature_group(
        name="karachi_air_quality",
        version=2,
        primary_key=["event_id"],  # ✅ String primary key
        event_time="timestamp",     # ✅ timestamp is event_time, NOT primary key
        online_enabled=False,
        description="Karachi AQI features with pollutants and time-based features"
    )
    
    # Insert data
    fg.insert(df)
    print(f"✅ Pushed {len(df)} records to Hopsworks Feature Store")