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
    print("🧠 Fetching / creating Feature View...")
    try:
        fv = fs.get_feature_view(
            name="karachi_air_quality_fv",
            version=1
        )
        print("📊 Using existing Feature View")
    except:
        fv = fs.create_feature_view(
            name="karachi_air_quality_fv",
            version=1,
            query=fg.select_all(),
            labels=["aqi"],
            description="AQI feature view for training"
        )
        print("🆕 Feature View created")

    # -----------------------
    # Training Dataset
    # -----------------------
    print("📦 Fetching / creating Training Dataset...")
    try:
        td = fv.get_training_dataset(version=1)
    except:
        td = fv.create_training_dataset(
            version=1,
            description="AQI training dataset"
        )

    # -----------------------
    # Read data
    # -----------------------
    print("📥 Reading training data (may take time)...")
    df = td.read()

    print(f"📈 Training rows: {df.shape[0]}")

    if df.shape[0] < 500:
        print("⚠️ Not enough data to train. Skipping.")
        return

    df = df.sort_values("timestamp").reset_index(drop=True)

    # -----------------------
    # Train → Evaluate → Save
    # -----------------------
    models, metrics = train_models(df)
    evaluate_models(metrics)
    save_models(models, metrics)

    print("✅ Daily training pipeline finished successfully")


if __name__ == "__main__":
    main()
