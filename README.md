

# 🌫️ Karachi AQI Predictor – ML Forecasting System

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)
![Hopsworks](https://img.shields.io/badge/Feature%20Store-Hopsworks-purple.svg)
![CI/CD](https://img.shields.io/badge/Automation-GitHub%20Actions-black.svg)

An **end-to-end production-grade MLOps system** that predicts Karachi’s Air Quality Index (AQI) for the next **72 hours (3 days)** using a fully automated **serverless architecture**.

Built during a Data Science internship at **10Pearls**, this system demonstrates modern ML engineering practices including:

* Automated feature pipelines
* Daily model retraining
* Model versioning
* CI/CD automation
* SHAP explainability
* Interactive real-time dashboard

---

# 🎯 Key Features

## ⚡ Automated Feature Pipeline (Hourly)

* Fetches weather & pollutant data from Open-Meteo
* Computes lag, rolling, and temporal features
* Engineers AQI change-rate features
* Stores versioned features in **Hopsworks Feature Store**
* Supports historical backfilling for training data

---

## 🤖 Automated Training & Model Registry (Daily)

* Models: Random Forest, Ridge Regression, Gradient Boosting
* Time-series optimized training split
* Automatic best model selection (RMSE-based)
* Evaluation metrics: RMSE, MAE, R²
* Model versioning via **Hopsworks Model Registry**

---

## 📊 Interactive Streamlit Dashboard

* Real-time AQI monitoring
* 3-day hourly AQI forecast
* Historical trend visualization
* Model performance display
* SHAP-based explainability
* Hazard-level AQI alerts

---

## 🔄 CI/CD Automation

* Hourly Feature Pipeline via GitHub Actions
* Daily Training Pipeline via GitHub Actions
* Automated retraining & model promotion
* Secrets securely managed via environment variables

---

# 🏗️ System Architecture

```
Open-Meteo API
      ↓
Feature Pipeline (Hourly)
      ↓
Hopsworks Feature Store
      ↓
Training Pipeline (Daily)
      ↓
Hopsworks Model Registry
      ↓
Streamlit Dashboard
```

---

# 🧠 Forecasting Objective

* **City:** Karachi
* **Granularity:** Hourly
* **Forecast Horizon:** 72 hours (3 days)
* **Approach:** Supervised time-series regression using engineered tabular features

Why 3-day forecasting?

72-hour forecasts are actionable for:

* Public health advisories
* Urban planning
* Pollution monitoring
* Early warning systems

---

# ⚙️ Feature Engineering

The system builds robust time-series features including:

### ⏳ Time-Based Features

* Hour of day
* Day of week
* Month
* Weekend indicator

### 📈 Lag Features

* Previous 1h, 6h, 24h AQI values
* Pollutant lag features

### 📊 Rolling Statistics

* 6-hour rolling averages
* 24-hour rolling averages
* Rolling standard deviation

### 🔁 Derived Features

* AQI change rate (delta)
* Wind-adjusted pollutant interaction

All features are stored in a versioned **Feature Store** to ensure reproducibility.

---

# 🏋️ Training Pipeline

Daily automated retraining includes:

1. Fetch historical features & targets from Feature Store
2. Perform train/validation/test split
3. Train multiple candidate models
4. Evaluate using:

   * RMSE
   * MAE
   * R²
5. Select best-performing model
6. Register model in Model Registry

Model artifacts are serialized using `joblib`.

---

# 📦 Artifacts

## `latest_features.parquet`

* Most recent engineered features
* Used for dashboard predictions
* Represents current state of the data pipeline

## `model.joblib`

* Serialized best-performing trained model
* Loaded by Streamlit app for inference
* Stored locally and/or registered in Model Registry

## `metrics.json`

* Stores latest RMSE, MAE, R² values
* Updated after each training run
* Displayed in dashboard

In simple terms:

* `latest_features.parquet` → **What to predict on**
* `model.joblib` → **How to predict**
* `metrics.json` → **How well it predicts**

---

# 📁 Project Structure

```
AQI_Predictor/
│
├─ .github/workflows/         # CI/CD automation
│  ├─ feature_pipeline.yml    # Hourly pipeline
│  └─ train_daily.yml         # Daily training
│
├─ artifacts/                 # Models & metrics
│
├─ src/
│  ├─ data_ingestion/         # API ingestion
│  ├─ features/               # Feature engineering
│  ├─ feature_store/          # Hopsworks integration
│  ├─ models/                 # Training & evaluation
│  ├─ Pipeline/               # Orchestration
│  └─ utils/                  # Shared utilities
│
├─ ui/                        # Streamlit dashboard
├─ scripts/                   # Helper scripts
├─ notebooks/                 # EDA & SHAP analysis
├─ requirements.txt
└─ README.md
```

---

# 🚀 Local Setup

## 1️⃣ Clone Repository

```bash
git clone <your-repo-url>
cd AQI_Predictor
```

---

## 2️⃣ Create Virtual Environment

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python -m venv venv
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Configure Environment Variables

### Windows

```powershell
$env:HOPSWORKS_API_KEY="your_api_key"
$env:HOPSWORKS_PROJECT_NAME="your_project"
```

### Or using `.env`

```env
HOPSWORKS_API_KEY=your_api_key
HOPSWORKS_PROJECT_NAME=your_project
```

---

# 🔄 Manual Pipeline Execution

## Run Feature Pipeline

```bash
python -m src.main
```

## Run Training Pipeline

```bash
python -m src.Pipeline.train_daily
```

---

# 📊 Launch Dashboard

```bash
cd ui
streamlit run app.py
```

The dashboard will display:

* Current AQI
* 3-day forecast
* Historical trends
* Model metrics
* Explainability visuals

---

# 🔬 Model Explainability

SHAP analysis provides:

* Global feature importance
* Local explanation per prediction
* Pollutant impact analysis
* Temporal feature influence

Explainability artifacts are stored for transparency and debugging.

---

# 🔐 Security

* API keys stored via environment variables
* No sensitive personal data
* Uses public environmental datasets

---

# 🐛 Troubleshooting

### Model Not Loading

* Verify Hopsworks credentials
* Check model registry version
* Ensure `model.joblib` exists in artifacts

### Pipeline Failure

* Check GitHub Actions logs
* Verify secrets configuration
* Confirm feature store connectivity

---

# 📈 Future Improvements

* Deep learning models (LSTM / Transformers)
* Multi-city forecasting
* Drift detection & monitoring
* SMS / Email AQI alerts
* Dockerized deployment
* Azure or GCP production hosting

---

# ✅ Final Deliverables

* Fully automated hourly feature pipeline
* Daily retraining & model versioning
* Serverless architecture
* Interactive dashboard
* SHAP explainability
* Reproducible MLOps workflow

---

**Last Updated: February 2026**

---

