# 🌫️ AQI Predictor

A machine learning-powered Air Quality Index (AQI) prediction system for Karachi. This project forecasts air quality levels using real-time meteorological data from Open-Meteo API, with features engineered and stored in Hopsworks, and predictions visualized through an interactive Streamlit dashboard.

---

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Components](#project-components)
- [Pipeline Architecture](#pipeline-architecture)
- [Dashboard](#dashboard)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

- **Real-time Data Ingestion**: Fetches meteorological data from Open-Meteo API
- **Automated Feature Engineering**: Builds and transforms features for model predictions
- **Hopsworks Integration**: Stores features in a distributed feature store for scalability
- **Machine Learning Models**: Trains and evaluates multiple models (scikit-learn based)
- **Daily Pipeline Automation**: Scheduled daily retraining with new data
- **Interactive Dashboard**: Streamlit-based UI for AQI predictions and analysis
- **Model Artifacts**: Persists trained models using joblib for inference
- **Explainability**: SHAP analysis for model interpretation
- **Data Profiling**: EDA and feature importance analysis using Jupyter notebooks

---

## 📂 Project Structure

```
AQI_Predictor/
├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
├── artifacts/                         # Model and metrics storage
│   ├── model.joblib                  # Trained ML model
│   └── metrics.json                  # Model performance metrics
├── scripts/                           # Utility scripts
│   └── export_latest_features.py     # Export features from feature store
├── src/                               # Main source code
│   ├── __init__.py
│   ├── main.py                       # Entry point for data pipeline
│   ├── data_ingestion/               # Data collection
│   │   └── fetch_openmeteo.py        # Open-Meteo API integration
│   ├── feature_store/                # Feature store operations
│   │   └── push_to_hopsworks.py      # Hopsworks integration
│   ├── features/                     # Feature engineering
│   │   └── build_features.py         # Feature transformation
│   ├── models/                       # Model operations
│   │   ├── __init__.py
│   │   ├── train_models.py           # Model training
│   │   ├── evaluate.py               # Model evaluation
│   │   └── save_model.py             # Model persistence
│   ├── notebooks/                    # Jupyter notebooks
│   │   ├── eda.ipynb                 # Exploratory data analysis
│   │   ├── feature_importance.csv    # Feature importance results
│   │   └── shap_analysis.ipynb       # SHAP model explainability
│   ├── Pipeline/                     # Orchestration
│   │   ├── __init__.py
│   │   └── train_daily.py            # Daily training scheduler
│   └── utils/                        # Utility functions
│       ├── config.py                 # Configuration management
│       └── metrics.py                # Metrics calculation
└── ui/                               # Streamlit dashboard
    ├── app.py                        # Main dashboard application
    ├── utils.py                      # Dashboard utilities
    └── requirements.txt              # Dashboard dependencies
```

---

## 📦 Prerequisites

- **Python**: 3.8 or higher
- **pip**: Package installer for Python
- **Git**: Version control (optional)
- **Environment Variables**: Hopsworks API key and project name

### Required API Credentials

1. **Hopsworks Account**: 
   - Sign up at [Hopsworks.ai](https://www.hopsworks.ai)
   - Create a new project
   - Generate an API key

2. **Environment Variables**:
   ```
   HOPSWORKS_API_KEY=your_api_key_here
   HOPSWORKS_PROJECT_NAME=your_project_name_here
   ```

---

## 🚀 Installation

### 1. Clone or Download the Repository

```bash
# Navigate to the project directory
cd AQI_Predictor
```

### 2. Create a Python Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install main project dependencies
pip install -r requirements.txt

# Install dashboard dependencies (optional, if running UI)
pip install -r ui/requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory:

```env
HOPSWORKS_API_KEY=your_api_key_here
HOPSWORKS_PROJECT_NAME=your_project_name_here
```

Alternatively, set environment variables in your system:

**Windows (PowerShell)**:
```powershell
$env:HOPSWORKS_API_KEY="your_api_key_here"
$env:HOPSWORKS_PROJECT_NAME="your_project_name_here"
```

**Windows (Command Prompt)**:
```cmd
set HOPSWORKS_API_KEY=your_api_key_here
set HOPSWORKS_PROJECT_NAME=your_project_name_here
```

**macOS/Linux**:
```bash
export HOPSWORKS_API_KEY="your_api_key_here"
export HOPSWORKS_PROJECT_NAME="your_project_name_here"
```

---

## ⚙️ Configuration

### Main Configuration (`src/utils/config.py`)

Review and modify configuration settings:

- **Data Ingestion**: API endpoints, polling intervals
- **Feature Engineering**: Feature calculations and transformations
- **Model Training**: Hyperparameters, test/train split
- **Feature Store**: Hopsworks feature group settings
- **Pipeline**: Scheduling and retry logic

### Example Configuration Update

```python
# src/utils/config.py
LOCATION = "Karachi"
FEATURE_GROUP_VERSION = 4
MODEL_VERSION = 1
BATCH_SIZE = 100
```

---

## 📖 Usage

### 1. Run the Data Pipeline

Fetch data, engineer features, and push to Hopsworks:

```bash
python -m src.main
```

**What it does**:
- Fetches hourly meteorological data from Open-Meteo API
- Engineers features (lag features, rolling averages, etc.)
- Pushes features to Hopsworks feature store
- Handles bootstrapping for initial data ingestion

### 2. Train the Model

Train or retrain the ML model:

```bash
python -m src.models.train_models
```

**What it does**:
- Reads features from Hopsworks
- Trains multiple models (Linear Regression, Random Forest, Gradient Boosting, etc.)
- Evaluates model performance
- Saves the best model to `artifacts/model.joblib`
- Logs metrics to `artifacts/metrics.json`

### 3. Launch the Streamlit Dashboard

Run the interactive dashboard for predictions and visualization:

```bash
cd ui
streamlit run app.py
```

**Dashboard Features**:
- Real-time AQI predictions
- Historical trends and visualizations
- AQI category indicators (Good, Moderate, Unhealthy, etc.)
- Model performance metrics
- Feature importance visualization
- Comparison charts

### 4. Run Daily Pipeline (Optional)

Schedule automated daily training and predictions:

```bash
python -m src.Pipeline.train_daily
```

---

## 🏗️ Project Components

### Data Ingestion (`src/data_ingestion/fetch_openmeteo.py`)

Fetches real-time weather data from the Open-Meteo API:

- Temperature
- Humidity
- Wind speed
- Precipitation
- Atmospheric pressure

### Feature Engineering (`src/features/build_features.py`)

Creates machine learning features from raw data:

- Lag features (previous hour, previous day)
- Rolling averages (6-hour, 24-hour windows)
- Time-based features (hour of day, day of week)
- Statistical features (standard deviation, min/max)

### Feature Store (`src/feature_store/push_to_hopsworks.py`)

Manages feature persistence and retrieval:

- Pushes engineered features to Hopsworks
- Handles versioning and backfill
- Ensures data consistency and integrity

### Model Training (`src/models/train_models.py`)

Trains multiple ML models and selects the best:

- Models: Linear Regression, Random Forest, Gradient Boosting, SVR
- Evaluation metrics: MAE, RMSE, R²
- Hyperparameter tuning
- Cross-validation

### Model Evaluation (`src/models/evaluate.py`)

Assesses model performance:

- Calculates performance metrics
- Generates evaluation reports
- Logs results for monitoring

### Model Persistence (`src/models/save_model.py`)

Saves and loads trained models:

- Uses joblib for serialization
- Manages model versioning
- Supports inference

---

## 🔄 Pipeline Architecture

```
Open-Meteo API → Data Ingestion → Feature Engineering → Hopsworks Feature Store
                                                              ↓
                                                      Model Training
                                                              ↓
                                                       Model Evaluation
                                                              ↓
                                                    Save Model Artifacts
                                                              ↓
                                                       Streamlit Dashboard
```

### Daily Pipeline Flow

1. **Data Collection** (7:00 AM): Fetch latest meteorological data
2. **Feature Engineering** (7:10 AM): Transform raw data into features
3. **Push to Feature Store** (7:15 AM): Store in Hopsworks
4. **Model Retraining** (8:00 AM): Train with latest data
5. **Metrics Calculation** (8:15 AM): Evaluate performance
6. **Dashboard Update** (8:30 AM): Reflect new predictions in UI

---

## 📊 Dashboard

### Key Pages

1. **Home**: Overview and latest AQI prediction
2. **Forecast**: 24-hour AQI forecast
3. **Historical Trends**: Past AQI values and patterns
4. **Model Performance**: Metrics and model comparison
5. **Feature Importance**: Top features affecting predictions
6. **About**: Project information and documentation

### Running the Dashboard

```bash
cd ui
streamlit run app.py
```

Access at: `http://localhost:8501`

---

## 🛠️ Development

### Project Setup for Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
pip install jupyter pytest black flake8
```

2. Explore data with Jupyter notebooks:
```bash
jupyter notebook src/notebooks/eda.ipynb
jupyter notebook src/notebooks/shap_analysis.ipynb
```

3. Run tests:
```bash
pytest tests/
```

### Code Style

- Use **Black** for code formatting
- Use **Flake8** for linting
- Follow PEP 8 conventions

### Adding New Features

1. Create feature engineering logic in `src/features/build_features.py`
2. Update Hopsworks schema if needed
3. Retrain models with new features
4. Test with evaluation metrics
5. Deploy via pipeline

---

## 🔍 Troubleshooting

### Issue: Hopsworks Connection Error

**Solution**:
- Verify API key and project name in `.env`
- Check internet connection
- Ensure Hopsworks API is accessible
- Review `src/main.py` error messages

### Issue: Model Not Found

**Solution**:
```bash
# Retrain the model
python -m src.models.train_models
```

### Issue: Dashboard Not Starting

**Solution**:
```bash
# Ensure Streamlit is installed
pip install streamlit

# Run with verbose logging
streamlit run ui/app.py --logger.level=debug
```

### Issue: Feature Store Push Failed

**Solution**:
- Check Hopsworks project quota
- Verify network connectivity
- Review logs in `src/feature_store/push_to_hopsworks.py`
- Increase retry count if needed

### Issue: Missing Dependencies

**Solution**:
```bash
# Reinstall all dependencies
pip install --upgrade -r requirements.txt
```

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Guidelines

- Write clear, descriptive commit messages
- Include docstrings in all functions
- Test changes before submitting
- Update documentation if needed
- Follow PEP 8 style guide

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Contact & Support

- **Project**: AQI Predictor
- **Purpose**: Air Quality Index prediction for Karachi
- **Organization**: 10Pearls
- **Status**: Active Development

For issues, questions, or suggestions, please open an issue in the repository.

---

## 🙏 Acknowledgments

- **Open-Meteo**: For providing free weather API
- **Hopsworks**: For feature store infrastructure
- **Streamlit**: For dashboard framework
- **scikit-learn**: For machine learning tools
- **SHAP**: For model explainability

---

**Last Updated**: January 31, 2026

---

### Quick Start Summary

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
# Edit .env with your Hopsworks credentials

# 3. Run the pipeline
python -m src.main

# 4. Train the model
python -m src.models.train_models

# 5. Launch dashboard
cd ui && streamlit run app.py
```

Access the dashboard at `http://localhost:8501`
