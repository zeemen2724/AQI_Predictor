import joblib
import os

def save_models(models, metrics, folder="models"):
    os.makedirs(folder, exist_ok=True)

    # Select best model based on R2
    best_model_name = max(metrics, key=lambda x: metrics[x]["R2"])
    best_model = models[best_model_name]

    path = os.path.join(folder, f"{best_model_name}.pkl")
    joblib.dump(best_model, path)

    print(f"💾 Saved best model '{best_model_name}' at {path}")
