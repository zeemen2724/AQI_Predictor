import os
os.environ["HOPSWORKS_DISABLE_MODEL_SERVING"] = "1"

from datetime import datetime, timedelta
import hopsworks
import pandas as pd
import time
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

from src.data_ingestion.fetch_openmeteo import fetch_openmeteo_data
from src.features.build_features import build_features
from src.feature_store.push_to_hopsworks import push_features

BOOTSTRAP = False  


def safe_read(fg, retries=3, wait=10):
    """Read from feature group with retry logic"""
    for i in range(retries):
        try:
            return fg.read()
        except Exception as e:
            print(f"⚠️ Read failed ({i+1}/{retries}): {e}")
            if i < retries - 1:
                time.sleep(wait)
            else:
                raise RuntimeError(f"Feature store read failed after {retries} attempts: {e}")


def save_backup(df, prefix="backup_features"):
    """Save dataframe as backup in case of insertion failure"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}.csv"
        df.to_csv(filename, index=False)
        logger.info(f"💾 Backup saved to {filename}")
        return filename
    except Exception as e:
        logger.error(f"Failed to save backup: {e}")
        return None


def main():
    print("🔄 Starting Open-Meteo AQI pipeline...")

    # Login to Hopsworks
    try:
        project = hopsworks.login(
            api_key_value=os.getenv("HOPSWORKS_API_KEY"),
            project=os.getenv("HOPSWORKS_PROJECT_NAME"),
        )
        fs = project.get_feature_store()
        print("✅ Successfully logged into Hopsworks")
    except Exception as e:
        logger.error(f"❌ Failed to login to Hopsworks: {e}")
        raise

    # Get or create feature group
    fg = fs.get_or_create_feature_group(
        name="karachi_air_quality",
        version=5,
        primary_key=["event_id"],
        event_time="timestamp",
        description="Karachi AQI hourly features from Open-Meteo",
        online_enabled=False
    )

    # ---------------------------
    # BOOTSTRAP MODE
    # ---------------------------
    if BOOTSTRAP:
        start = (datetime.utcnow() - timedelta(days=365)).strftime("%Y-%m-%d")
        end = datetime.utcnow().strftime("%Y-%m-%d")

        print(f"🆕 Bootstrapping {start} → {end}")
        df_raw = fetch_openmeteo_data(start, end)

    # ---------------------------
    # INCREMENTAL MODE
    # ---------------------------
    else:
        df_hist = safe_read(fg)
    
        if df_hist.empty:
            print("🟡 Feature store empty — run BOOTSTRAP mode first")
            print("   Set BOOTSTRAP = True in main.py")
            return
    
        last_ts = df_hist["timestamp"].max()
        print(f"⏱️ Last timestamp in FS: {last_ts}")
    
        start = last_ts.strftime("%Y-%m-%d")
        end = datetime.utcnow().strftime("%Y-%m-%d")
        
        df_raw = fetch_openmeteo_data(
            start_date=start,
            end_date=end
        )

        if df_raw.empty:
            print("🟡 No new Open-Meteo data")
            return

    # ---------------------------
    # BUILD FEATURES
    # ---------------------------
    if BOOTSTRAP:
        df_features = build_features(df_raw)
    else:
        last_ts = safe_read(fg)["timestamp"].max()
        print(f"⏱️ Last timestamp in FS: {last_ts}")
    
        df_new = df_raw[df_raw["timestamp"] > last_ts]
    
        if df_new.empty:
            print("🟡 No new data to ingest. Skipping insert.")
            return
    
        df_features = build_features(df_new)
    
    if df_features.empty:
        print("🟡 No features generated")
        return
    
    print(f"📊 Generated {len(df_features)} feature rows")
    
    # ---------------------------
    # PUSH TO HOPSWORKS
    # ---------------------------
    try:
        push_features(fg, df_features)
        
        # Save local copy on success
        df_features.to_parquet("latest_features.parquet", index=False)
        print("💾 Features saved locally to latest_features.parquet")
        
        print("✅ Pipeline finished successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to push features: {e}")
        
        # Save backup
        backup_file = save_backup(df_features)
        
        logger.error("Pipeline failed during feature insertion")
        logger.info(f"Data preserved in: {backup_file or 'latest_features.parquet (if exists)'}")
        
        # Re-raise to fail the pipeline
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"💥 Pipeline failed with error: {e}")
        exit(1)