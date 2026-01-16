import os
import hopsworks
import pandas as pd

from src.model.train_models import train_models
from src.model.evaluate import evaluate_models
from src.model.save_models import save_models

def main():
    print("🚀 Starting DAILY training pipeline...")

    # Login to Hopsworks
    project = hopsworks.login(
        api_key_value=os.getenv("HOPSWORKS_API_KEY"),
        project=os.getenv("HOPSWORKS_PROJECT_NAME")
    )
    fs = project.get_feature_store()

    # Read feature group
    fg = fs.get_feature_group(
        name="karachi_air_quality",
        version=2
    )
    print("📥 Reading features from Hopsworks...")
    df = fg.read()

    if df.shape[0] < 500:
        print("⚠️ Not enough data to train. Skipping.")
        return

    df = df.sort_values("timestamp").reset_index(drop=True)

    # Train models
    models, metrics = train_models(df)

    # Evaluate models
    evaluate_models(metrics)

    # Save best model
    save_models(models, metrics)

    print("✅ Daily training pipeline finished successfully")


if __name__ == "__main__":
    main()
