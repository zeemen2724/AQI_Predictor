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
    # Feature Group
    # -----------------------
    print("📊 Fetching Feature Group...")
    fg = fs.get_feature_group(
        name="karachi_air_quality",
        version=3
    )

    # -----------------------
    # Feature View
    # -----------------------
    print("🧠 Creating/Fetching Feature View...")
    
    # Use get_or_create_feature_view for safer handling
    fv = fs.get_or_create_feature_view(
        name="karachi_air_quality_fv",
        version=1,
        query=fg.select_all(),
        labels=["aqi"],
        description="AQI feature view for training"
    )
    
    if fv is None:
        raise RuntimeError("❌ Feature View creation failed")
    
    print("✅ Feature View ready")

    # -----------------------
    # Read Data Directly
    # -----------------------
    print("📥 Reading data from Feature View...")
    
    # Read directly from feature view (simpler than training dataset)
    df = fv.get_batch_data()
    
    print(f"📈 Total rows: {df.shape[0]}")

    if df.shape[0] < 500:
        print("⚠️ Not enough data to train. Skipping.")
        return

    # Sort by timestamp for time-series split
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