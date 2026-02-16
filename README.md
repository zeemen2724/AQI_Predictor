# AQI Predictor — Serverless Air Quality Forecasting System

Production-ready project that forecasts the Air Quality Index (AQI) for the next
3 days using a 100% serverless ML stack. The system ingests weather and pollutant
data, computes robust time-series and derived features, trains and registers
models, and serves forecasts via a lightweight web application. Designed for
reproducibility, automation and easy portfolio demonstration.

---

**Contents**

- Project overview and forecasting objective
- System architecture and dataflow
- Feature & training pipelines
- Explainability, CI/CD, and web application details
- Tech stack, folder layout, run instructions, and future work

---

## 1. Project Overview

- Purpose: Provide 3-day AQI forecasts (hourly granularity) for a city
  using meteorological and pollutant inputs.
- Forecast horizon: short-term forecasting for the next 72 hours (3 days).
- Serverless approach: ingestion, feature computation, training orchestration,
  and serving are implemented using serverless components (cloud functions,
  managed feature store, model registry and CI/CD). This minimizes infra
  management while enabling autoscaling and cost-efficiency.

Why 3-day forecasts?
- 72-hour forecasts are actionable for public advisories, planning, and
  health-based alerts while still tractable with tabular/time-series models.

---

## 2. System Architecture

High-level components and how data flows through the system:

- Ingestion (serverless functions / scheduled jobs)
- Feature pipeline (transformation, feature store writes)
- Training pipeline (fetch features → train → evaluate)
- Model registry (versioned model artifacts + metadata)
- CI/CD automation (GitHub Actions / orchestrator)
- Web application (Streamlit + lightweight API for real-time serving)

Dataflow:
1. External APIs (Open-Meteo, pollutant data providers) → ingestion layer.
2. Raw data passed to Feature Pipeline which computes time-based and derived
   features and writes feature rows to a Feature Store (Hopsworks or Vertex AI).
3. Training pipeline pulls historical feature sets from the Feature Store,
   trains multiple candidate models, logs experiments and metrics, and pushes
   the best model to a Model Registry.
4. Web app and serverless inference components load the registered model and
   read recent features from the Feature Store for real-time 3-day forecasts.

Diagram (logical):

External APIs → Ingestion → Feature Pipeline → Feature Store → Training → Model Registry → Serving → Web App

---

## 3. Feature Pipeline

Responsibilities and capabilities:

- Sources: weather APIs (temperature, humidity, wind, pressure), pollutant
  APIs (PM2.5, PM10, NO2, O3), and any local sensors.
- Time-based features: hour-of-day, day-of-week, month, is_weekend, seasonal
  encodings.
- Derived features: rolling averages (6h, 24h), lag features, AQI change-rate
  (delta over previous hour/day), diurnal differences, wind-adjusted indices.
- Target engineering: compute target AQI labels for +24h, +48h, +72h horizons
  and store alongside features.
- Storage: write feature rows and targets to a Feature Store (Hopsworks or
  Vertex AI Feature Store) with versioning and partitioning by date.
- Backfill: support historical backfill runs to rebuild training datasets for
  model development and re-training.

Operational notes:
- Idempotent writes: ensure feature pipeline is idempotent for retries.
- Schema registry / validation in the Feature Store to maintain compatibility.

---

## 4. Training Pipeline

Key steps implemented in the pipeline:

- Data retrieval: fetch historical features and targets from the Feature Store
  for selected date ranges and partitions.
- Candidate models: Random Forest, Ridge Regression, Gradient Boosting (e.g.
  XGBoost/LightGBM), and baseline models for comparison.
- Training workflow: data splits (train/val/test), hyperparameter search,
  cross-validation and model selection.
- Evaluation metrics: RMSE, MAE, R² reported per-horizon (+24h, +48h, +72h).
- Experiment tracking: use MLflow / built-in logging to record runs, params,
  artifacts and evaluation metrics.
- Model Registry: the selected best model (by validation metric) is serialized
  (joblib/pickle) and stored with metadata (version, metrics, feature schema)
  in a Model Registry (Hopsworks Model Registry or Vertex Model Registry).

Automation & reliability:
- Retraining is scheduled (daily) with monitored runs, automatic rollback on
  degraded performance, and promotion to production via CI gates.

---

## 5. Model Explainability

- Approach: SHAP values for feature importance and per-prediction explanations.
- Usage: compute global feature importance (summary plots) and local SHAP
  explanations for specific forecast timestamps.
- Integration: SHAP outputs are stored alongside predictions (or visualized in
  the dashboard) to assist debugging and stakeholder interpretability.

Notes:
- For models without fast SHAP support, use approximate SHAP methods or LIME.
- Persist explanation artifacts for auditability of model decisions.

---

## 6. CI/CD & Automation

Pipeline cadence and orchestration:

- Feature pipeline: runs hourly (or configurable frequency) to keep features
  fresh for serving and near-real-time ingestion.
- Training pipeline: runs daily to retrain models with newly backfilled data.
- Orchestration & CI: implemented using GitHub Actions for CI and a scheduler
  (Airflow / Cloud Scheduler) for production orchestration. GitHub Actions
  handles unit tests, linting, and deployment triggers for serverless functions.
- Retraining workflow: automated training → evaluation → automated tests →
  model promotion to registry when passing thresholds.

Reliability features:
- Canary testing, metric-based promotion, alerts and logging for failed runs.

---

## 7. Web Application

Stack & responsibilities:

- Frontend: Streamlit dashboard for visualization and user interaction.
- Optional lightweight API: FastAPI for serving predictions to external clients.
- Data: reads latest features from Feature Store, loads models from Model
  Registry, and produces 3-day hourly forecasts.

Dashboard provides:
- Current (real-time) AQI and predicted AQI for the next 72 hours
- Visualizations: time series plots, confidence bands, feature importance
- Alerts: thresholds for hazardous AQI levels and simple notification hooks
- Explainability view: per-prediction SHAP contributions

Run locally (example):

```bash
cd ui
streamlit run app.py
```

Production considerations:
- Cache recent predictions for fast UI load and use serverless endpoints for
  on-demand prediction if needed.

---

## 8. Tech Stack

- Language: Python 3.8+
- ML: scikit-learn, XGBoost / LightGBM
- Explainability: SHAP (or LIME as fallback)
- Feature Store / Model Registry: Hopsworks or Google Vertex AI
- Orchestration & CI: GitHub Actions, Airflow (or Cloud Scheduler)
- Web: Streamlit (with optional FastAPI)
- Data & utilities: pandas, numpy, joblib, matplotlib/plotly

---

## 9. Project Structure

```
AQI_Predictor/
├─ artifacts/                # persisted models & metrics (model.joblib, metrics.json)
├─ src/
│  ├─ data_ingestion/        # API clients and ingestion functions
│  ├─ features/              # feature engineering and transformations
│  ├─ feature_store/         # adapters for Hopsworks / Vertex Feature Store
│  ├─ models/                # training, evaluation, model selection
│  ├─ Pipeline/              # orchestration helpers and scheduled jobs
│  └─ utils/                 # config, metrics, and shared utilities
├─ ui/                       # Streamlit app and UI utilities
├─ scripts/                  # helper scripts (export features, backfill)
├─ notebooks/                # EDA and analysis (SHAP, feature importance)
├─ requirements.txt          # main dependencies
└─ README.md                 # this document
```

Purpose highlights:
- `src/data_ingestion`: connectors to external APIs and data validation
- `src/features`: deterministic transforms, lag/rolling features and targets
- `src/feature_store`: read/write helpers and schema registration
- `src/models`: training loops, experiment logging and model export
- `ui/app.py`: dashboard entry point

---

## 10. How to Run the Project (local development)

1) Create and activate virtual environment (Windows):

```powershell
python -m venv venv
venv\\Scripts\\activate
```

2) Install dependencies:

```bash
pip install -r requirements.txt
pip install -r ui/requirements.txt    # UI dependencies (optional)
```

3) Configure environment variables (example for Hopsworks):

```powershell
$env:HOPSWORKS_API_KEY = "your_api_key"
$env:HOPSWORKS_PROJECT_NAME = "your_project"
```

4) Run ingestion / feature pipeline (local run or scheduled cloud function):

```bash
python -m src.main
```

5) Train models (local run):

```bash
python -m src.models.train_models
```

6) Launch UI locally:

```bash
cd ui
streamlit run app.py
```

---

## 11. Future Improvements

- Add deep learning models (LSTM/Transformer) for longer-range forecasting
- Multi-city and regional forecasting with transfer-learning techniques
- Containerized deployment (`Dockerfile`) and Kubernetes for non-serverless
  advanced deployments
- Integrate alerting (SMS, Email) and policy-driven triggers
- Add robust model monitoring and drift detection (production metrics)

---

## 12. Final Deliverables

- End-to-end serverless ML system for 3-day AQI forecasting
- Automated hourly feature pipeline and daily retraining pipeline
- Versioned Model Registry and experiment logs
- Interactive Streamlit dashboard with real-time forecasts and explainability
- Notebook analyses and a reproducible development environment

---

If you'd like, I can add:
- CI badges for build/test coverage
- A `LICENSE` file (MIT/Apache)
- A short CONTRIBUTING guide and a `deploy` script

File references: [src/main.py](src/main.py) • [src/models/train_models.py](src/models/train_models.py) • [ui/app.py](ui/app.py)

