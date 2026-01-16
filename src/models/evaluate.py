def evaluate_models(metrics):
    print("📊 Model evaluation:")
    for model_name, metric in metrics.items():
        print(f"--- {model_name} ---")
        for k, v in metric.items():
            print(f"{k}: {v:.4f}")
