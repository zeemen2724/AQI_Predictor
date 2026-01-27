import joblib
import os

def save_models(models, metrics, folder="artifacts"):
    os.makedirs(folder, exist_ok=True)

    # Select best model based on RMSE (uppercase)
    best_model_name = min(metrics, key=lambda x: metrics[x]["RMSE"])
    best_model = models[best_model_name]

    path = os.path.join(folder, "model.joblib")
    joblib.dump(best_model, path)

    print(f"Saved best model \"{best_model_name}\" at {path}")
