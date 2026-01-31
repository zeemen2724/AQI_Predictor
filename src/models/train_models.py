import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


from src.features.feature_engineering import create_lag_features, FEATURES, TARGET


# ===========================
# TRAINING
# ===========================
def train_models(df):
    """
    df must have columns: timestamp, aqi (raw historical data).
    This function runs feature engineering internally, then trains.
    """
    df = create_lag_features(df)  # adds lag + time features, drops NaN rows

    X = df[FEATURES]
    y = df[TARGET]

    # ⏳ Time-aware split (NO shuffle — order matters for time series)
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    models = {}
    metrics = {}

    # ---------------------------
    # Linear Regression
    # ---------------------------
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    y_pred = lr.predict(X_test)

    metrics["LinearRegression"] = {
        "MAE": mean_absolute_error(y_test, y_pred),
        "RMSE": mean_squared_error(y_test, y_pred) ** 0.5,
        "R2": r2_score(y_test, y_pred),
    }
    models["LinearRegression"] = lr

    # ---------------------------
    # Random Forest
    # ---------------------------
    rf = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)

    metrics["RandomForest"] = {
        "MAE": mean_absolute_error(y_test, y_pred),
        "RMSE": mean_squared_error(y_test, y_pred) ** 0.5,
        "R2": r2_score(y_test, y_pred),
    }
    models["RandomForest"] = rf

    # ---------------------------
    # Gradient Boosting
    # ---------------------------
    gb = GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )
    gb.fit(X_train, y_train)
    y_pred = gb.predict(X_test)

    metrics["GradientBoosting"] = {
        "MAE": mean_absolute_error(y_test, y_pred),
        "RMSE": mean_squared_error(y_test, y_pred) ** 0.5,
        "R2": r2_score(y_test, y_pred),
    }
    models["GradientBoosting"] = gb

    print("✅ Forecasting models trained successfully.")
    return models, metrics