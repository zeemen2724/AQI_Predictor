import joblib
import os
import json

def save_models(models, metrics, folder="artifacts"):
    os.makedirs(folder, exist_ok=True)

    # Pick best model based on RMSE
    best_model_name = min(metrics, key=lambda x: metrics[x]["RMSE"])
    best_model = models[best_model_name]

    # Save model
    model_path = os.path.join(folder, "model.joblib")
    joblib.dump(best_model, model_path)

    # Save metrics
    metrics_path = os.path.join(folder, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)

    print(f"💾 Model saved: {model_path}")
    print(f"📊 Metrics saved: {metrics_path}")
    print(f"🏆 Best model: {best_model_name}")
