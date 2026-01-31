from datetime import timedelta
import numpy as np

def generate_forecast(historical_df, model, days=3):
    """
    Iterative multi-step AQI forecast (hourly)
    """
    if historical_df is None or historical_df.empty:
        return None

    hours = days * 24

    # Start from last known row
    last_row = historical_df.iloc[-1].copy()
    forecasts = []

    for step in range(hours):
        # Prepare model input
        X = last_row.drop(
            labels=["aqi", "timestamp", "event_id"],
            errors="ignore"
        ).to_frame().T

        # Predict AQI
        aqi_pred = float(model.predict(X)[0])

        # Create next timestep
        next_row = last_row.copy()
        next_row["timestamp"] = last_row["timestamp"] + timedelta(hours=1)
        next_row["aqi_predicted"] = aqi_pred

        # 🔁 Update lag features (VERY IMPORTANT)
        if "pm2_5_lag1" in last_row:
            next_row["pm2_5_lag2"] = last_row.get("pm2_5_lag1")
            next_row["pm2_5_lag1"] = last_row.get("pm2_5")

        if "pm2_5_roll3" in last_row:
            next_row["pm2_5_roll3"] = np.mean([
                last_row.get("pm2_5"),
                last_row.get("pm2_5_lag1"),
                last_row.get("pm2_5_lag2"),
            ])

        forecasts.append({
            "timestamp": next_row["timestamp"],
            "aqi_predicted": aqi_pred
        })

        # Move forward
        last_row = next_row

    return pd.DataFrame(forecasts)
