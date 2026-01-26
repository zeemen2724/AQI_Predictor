import os
os.environ["HOPSWORKS_DISABLE_MODEL_SERVING"] = "1"

from dotenv import load_dotenv
load_dotenv()

import hopsworks
import pandas as pd

from src.models.train_models import train_models
from src.models.evaluate import evaluate_models
from src.models.save_model import save_models


def main():
    print("🚀 Starting DAILY training pipeline...")

    # -----------------------
    # Login
    # -----------------------
    project = hopsworks.login(
        api_key_value=os.getenv("HOPSWORKS_API_KEY"),
        project=os.getenv("HOPSWORKS_PROJECT_NAME"),
    )
    fs = project.get_feature_store()

    # -----------------------
    # Feature Group v3
    # -----------------------
    print("📊 Fetching Feature Group v3...")
    fg = fs.get_feature_group(
        name="karachi_air_quality",
        version=3
    )

    # -----------------------
    # Feature View v2 (includes aqi)
    # -----------------------
    print("🧠 Creating/Fetching Feature View v2...")
    
    fv = fs.get_or_create_feature_view(
        name="karachi_air_quality_fv",
        version=2,  # ✅ v2 without labels parameter
        query=fg.select_all(),
        description="AQI feature view - all columns including aqi for manual train/test split"
    )
    
    if fv is None:
        raise RuntimeError("❌ Feature View creation failed")
    
    print("✅ Feature View v2 ready")

    # -----------------------
    # Read Data
    # -----------------------
    print("📥 Reading all data from Feature Store...")
    df = fv.get_batch_data()
    
    print(f"📈 Total rows: {df.shape[0]}")
    print(f"📋 Columns: {list(df.columns)}")

    # Verify aqi exists
    if 'aqi' not in df.columns:
        raise ValueError(f"❌ 'aqi' column missing! Available: {list(df.columns)}")

    # Minimum data check
    if df.shape[0] < 500:
        print("⚠️ Not enough data to train. Skipping.")
        return

    # Sort by timestamp for proper time-series split
    df = df.sort_values("timestamp").reset_index(drop=True)

    # -----------------------
    # Train → Evaluate → Save
    # -----------------------
    print("🔧 Training models...")
    models, metrics = train_models(df)
    
    print("📊 Evaluating models...")
    evaluate_models(metrics)
    
    print("💾 Saving best model...")
    save_models(models, metrics)

    print("✅ Daily training pipeline finished successfully")


if __name__ == "__main__":
    main()