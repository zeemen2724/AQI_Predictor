from src.models.train_models import train_models
from src.models.evaluate import evaluate_models
from src.models.save_model import save_models

def main():
    print("🚀 Starting DAILY training pipeline...")

    project = hopsworks.login(
        api_key_value=os.getenv("HOPSWORKS_API_KEY"),
        project=os.getenv("HOPSWORKS_PROJECT_NAME")
    )
    fs = project.get_feature_store()

    # Get Feature Group
    fg = fs.get_feature_group(
        name="karachi_air_quality",
        version=3
    )

    # Get or create Feature View
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

    # Get Training Dataset
    try:
        td = fv.get_training_dataset(version=1)
    except:
        td = fv.create_training_dataset(
            description="AQI training dataset",
            version=1
        )

    print("📥 Reading training data...")
    df = td.read()

    if df.shape[0] < 500:
        print("⚠️ Not enough data to train. Skipping.")
        return

    df = df.sort_values("timestamp").reset_index(drop=True)

    models, metrics = train_models(df)
    evaluate_models(metrics)
    save_models(models, metrics)

    print("✅ Daily training pipeline finished successfully")
