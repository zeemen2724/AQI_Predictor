import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
import hopsworks
import os
from dotenv import load_dotenv
import numpy as np
import joblib
import json
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

# ===========================
# ✅ FIX: Import the CORRECT recursive forecast from utils.py
#    (the old inline generate_forecast() in this file has been removed)
# ===========================
from utils import generate_forecast

# ===========================
# PAGE CONFIGURATION
# ===========================
st.set_page_config(
    page_title="Karachi AQI Predictor",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/karachi-aqi-predictor',
        'Report a bug': 'https://github.com/your-repo/karachi-aqi-predictor/issues',
        'About': "# Karachi AQI Predictor\nML-powered air quality prediction using GradientBoosting."
    }
)

# ===========================
# CUSTOM STYLING - DARK THEME WITH RIGHT SIDEBAR
# ===========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    /* Dark theme base */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
        color-scheme: dark !important;
        background-color: #0f1419 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main app container layout */
    [data-testid="stApp"] {
        display: block !important;
    }
    
    /* Main content area - leaves 30% gap on right for the fixed sidebar */
    [data-testid="stAppViewContainer"] {
        background-color: #0f1419 !important;
        width: calc(100vw - 30%) !important;
        max-width: calc(100vw - 30%) !important;
        margin-right: 30% !important;
        overflow-y: auto !important;
    }
    
    .main {
        background: #0f1419 !important;
        padding: 0 !important;
    }
    
    .block-container {
        padding: 1.5rem 2rem !important;
        max-width: 100%;
        background: #1a1f2e;
        border-radius: 16px;
        margin: 1rem auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* ============================================================
       SIDEBAR - fixed on the right, always open, no toggle at all
       ============================================================ */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-left: 2px solid #e0e0e0 !important;
        width: 30vw !important;
        min-width: 30vw !important;
        max-width: 30vw !important;
        height: 100vh !important;
        position: fixed !important;
        right: 0 !important;
        top: 0 !important;
        z-index: 999999 !important;
        overflow-y: auto !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
        transform: none !important;
        -webkit-transform: none !important;
    }
    
    /* Sidebar wrapper */
    [data-testid="stSidebar"] > div {
        margin: 0 !important;
        padding: 1.5rem !important;
        width: 100% !important;
    }
    
    /* ============================================================
       HIDE EVERY TOGGLE / COLLAPSE / MINIMIZE / MAXIMIZE BUTTON
       ============================================================ */
    [data-testid="collapsedControl"],
    [data-testid="collapsibleButton"],
    button[kind="header"],
    [data-testid="stSidebarNav"],
    .css-6qob1r,
    .css-1wbdfcn,
    [data-testid="stApp"] > button,
    [data-testid="stSidebar"] button[data-testid="toggleSidebarButton"],
    section[data-testid="stSidebar"] ~ div button,
    .stSidebar .css-1wbdfcn {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
        pointer-events: none !important;
        position: absolute !important;
        opacity: 0 !important;
    }
    
    /* Sidebar text colors - Dark for contrast on white */
    [data-testid="stSidebar"] {
        color: #1a1a1a !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #333333 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #1a1a1a !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #667eea !important;
        font-weight: 700;
        font-size: 1.3rem;
        margin-bottom: 0.5rem;
    }
    
    [data-testid="stSidebar"] .stMarkdown strong {
        color: #333333 !important;
        font-weight: 700;
    }
    
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stCaption {
        color: #555555 !important;
    }
    
    [data-testid="stSidebar"] .stMetric {
        background: #f5f5f5 !important;
        padding: 0.8rem !important;
        border-radius: 8px !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    [data-testid="stSidebar"] hr {
        border-color: #e0e0e0 !important;
        margin: 1rem 0;
    }
    
    [data-testid="stSidebar"] .stButton button {
        background: #667eea !important;
        color: white !important;
        border: none !important;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        width: 100%;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: #5568d3 !important;
        opacity: 0.9;
    }
    
    /* Hero Header - Dark themed */
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .hero-title {
        font-size: 2rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        color: white;
    }
    
    .hero-subtitle {
        font-size: 1rem;
        margin: 0 0 1rem 0;
        opacity: 0.95;
        color: white;
    }
    
    .status-info {
        font-size: 0.9rem;
        display: flex;
        gap: 1.5rem;
        flex-wrap: wrap;
        color: white;
    }
    
    /* Metric Cards - Dark themed */
    .metric-box {
        background: #252d3d;
        padding: 1.8rem 1.2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    .metric-label {
        font-size: 0.7rem;
        font-weight: 700;
        color: #a0adc7;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.8rem;
    }
    
    .metric-value {
        font-size: 3.2rem;
        font-weight: 700;
        line-height: 1;
        margin: 0.6rem 0;
        color: #667eea;
    }
    
    .metric-desc {
        font-size: 0.95rem;
        font-weight: 600;
        margin-top: 0.6rem;
        color: #e0e0e0;
    }
    
    /* Forecast Cards - Dark themed */
    .forecast-card {
        background: #252d3d;
        padding: 1.2rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        border-left: 4px solid;
        border-top: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    /* Section Headers - Light text on dark */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #e0e0e0;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #667eea;
    }
    
    /* Alert Boxes */
    .alert-box {
        background: #dc3545;
        color: white !important;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        font-weight: 500;
        border: 1px solid rgba(220, 53, 69, 0.5);
    }
    
    .alert-box * {
        color: white !important;
    }
    
    .warning-box {
        background: #f39c12;
        color: white !important;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        font-weight: 500;
        border: 1px solid rgba(243, 156, 18, 0.5);
    }
    
    .warning-box * {
        color: white !important;
    }
    
    /* Tabs - Dark themed */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #252d3d;
        padding: 0.5rem;
        border-radius: 8px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 0.7rem 1.5rem;
        font-weight: 600;
        background: transparent;
        color: #a0adc7 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #667eea !important;
        color: white !important;
    }
    
    /* Info boxes - Dark themed */
    div[data-testid="stInfo"] {
        background: rgba(102, 126, 234, 0.15);
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        color: #e0e0e0 !important;
    }
    
    div[data-testid="stInfo"] * {
        color: #e0e0e0 !important;
    }
    
    /* Success boxes - Dark themed */
    div[data-testid="stSuccess"] {
        background: rgba(16, 185, 129, 0.15);
        border-left: 4px solid #10b981;
        border-radius: 8px;
        color: #e0e0e0 !important;
    }
    
    div[data-testid="stSuccess"] * {
        color: #e0e0e0 !important;
    }
    
    /* Warning boxes - Dark themed */
    div[data-testid="stWarning"] {
        background: rgba(251, 191, 36, 0.15);
        border-left: 4px solid #fbbf24;
        border-radius: 8px;
        color: #e0e0e0 !important;
    }
    
    div[data-testid="stWarning"] * {
        color: #e0e0e0 !important;
    }
    
    /* Error boxes - Dark themed */
    div[data-testid="stError"] {
        background: rgba(239, 68, 68, 0.15);
        border-left: 4px solid #ef4444;
        border-radius: 8px;
        color: #e0e0e0 !important;
    }
    
    div[data-testid="stError"] * {
        color: #e0e0e0 !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    }
    
    /* Text colors - Light on dark */
    body {
        color: #e0e0e0;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #e0e0e0 !important;
    }
    
    p, span, label {
        color: #c0c0c0 !important;
    }
    
    .stCaption {
        color: #808080 !important;
    }
    
    /* Divider */
    hr {
        border-color: #3a4250 !important;
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# JS: Lock sidebar open & kill all toggle buttons permanently
# ===========================
st.markdown("""
<script>
(function() {
    function fixSidebar() {
        var sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.style.transform   = 'none';
            sidebar.style.visibility  = 'visible';
            sidebar.style.display     = 'block';
            sidebar.style.opacity     = '1';
            sidebar.style.width       = '30vw';
            sidebar.style.minWidth    = '30vw';
            sidebar.style.maxWidth    = '30vw';
            sidebar.style.position    = 'fixed';
            sidebar.style.right       = '0';
            sidebar.style.top         = '0';
            sidebar.style.height      = '100vh';
            sidebar.style.zIndex      = '999999';
        }

        var selectors = [
            '[data-testid="collapsedControl"]',
            '[data-testid="collapsibleButton"]',
            'button[kind="header"]',
            '[data-testid="stSidebarNav"]',
            '.css-6qob1r',
            '.css-1wbdfcn'
        ];
        selectors.forEach(function(sel) {
            document.querySelectorAll(sel).forEach(function(el) {
                el.style.display       = 'none';
                el.style.visibility    = 'hidden';
                el.style.width         = '0';
                el.style.height        = '0';
                el.style.overflow      = 'hidden';
                el.style.opacity       = '0';
                el.style.position      = 'absolute';
                el.style.pointerEvents = 'none';
            });
        });

        document.querySelectorAll('button').forEach(function(btn) {
            if (btn.querySelector('svg') && !btn.closest('[data-testid="stSidebar"]')) {
                var rect = btn.getBoundingClientRect();
                if (rect.width < 60 && rect.height < 60) {
                    btn.style.display = 'none';
                }
            }
        });
    }

    fixSidebar();

    var observer = new MutationObserver(function() { fixSidebar(); });
    observer.observe(document.documentElement, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['style', 'class']
    });
})();
</script>
""", unsafe_allow_html=True)

# ===========================
# HELPER FUNCTIONS
# ===========================
def get_aqi_category_info(aqi_value: float):
    """Get category label and color for an AQI value."""
    if aqi_value <= 50:
        return "Good 😌", "#00e400"
    elif aqi_value <= 100:
        return "Moderate 🙂", "#ffff00"
    elif aqi_value <= 150:
        return "Unhealthy for Sensitive 😐", "#ff7e00"
    elif aqi_value <= 200:
        return "Unhealthy 😷", "#ff0000"
    elif aqi_value <= 300:
        return "Very Unhealthy 🤢", "#8f3f97"
    else:
        return "Hazardous ☠️", "#7e0023"

def get_health_recommendation(aqi_value: float) -> str:
    """Get health recommendation based on AQI value."""
    if aqi_value > 200:
        return "Avoid outdoor activities. Wear N95 mask if necessary. Keep windows closed."
    elif aqi_value > 150:
        return "Sensitive groups should limit outdoor exposure. Consider using air purifiers."
    elif aqi_value > 100:
        return "Unusually sensitive individuals should consider limiting prolonged outdoor exertion."
    else:
        return "Air quality is acceptable for most people. Enjoy outdoor activities!"

@st.cache_data
def load_historical_data():
    """Load historical AQI data from Hopsworks Feature Store."""
    try:
        project = hopsworks.login(api_key_value=os.getenv("HOPSWORKS_API_KEY"))
        fs = project.get_feature_store()
        
        fg = fs.get_feature_group("karachi_air_quality", version=5)
        df = fg.read()
        
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        if "hour" not in df.columns:
            df["hour"] = df["timestamp"].dt.hour
        if "day" not in df.columns:
            df["day"] = df["timestamp"].dt.day
        if "month" not in df.columns:
            df["month"] = df["timestamp"].dt.month
        if "weekday" not in df.columns:
            df["weekday"] = df["timestamp"].dt.weekday
        
        return df.sort_values("timestamp")
    except Exception as e:
        st.error(f"⚠️ Unable to load air quality data: {str(e)}")
        st.stop()

@st.cache_resource
def get_model_metadata():
    """Get model metadata from artifacts directory."""
    metadata = {
        "name": "GradientBoosting",
        "best_model": "GradientBoosting",
        "mae": 0.2776,
        "rmse": 2.0713,
        "r2": 0.9976,
        "status": "✅ Model Loaded"
    }
    
    try:
        project_root = Path(__file__).parent.parent
        metrics_path = project_root / "artifacts" / "metrics.json"
        
        if metrics_path.exists():
            with open(metrics_path, 'r') as f:
                loaded_metrics = json.load(f)
                
                if 'GradientBoosting' in loaded_metrics:
                    gb_metrics = loaded_metrics['GradientBoosting']
                    metadata.update({
                        "mae": gb_metrics.get('MAE', metadata['mae']),
                        "rmse": gb_metrics.get('RMSE', metadata['rmse']),
                        "r2": gb_metrics.get('R2', metadata['r2']),
                        "best_model": loaded_metrics.get('best_model', 'GradientBoosting')
                    })
                else:
                    metadata.update({
                        "mae": loaded_metrics.get('mae', metadata['mae']),
                        "rmse": loaded_metrics.get('rmse', metadata['rmse']),
                        "r2": loaded_metrics.get('r2', metadata['r2']),
                        "best_model": loaded_metrics.get('best_model', 'GradientBoosting')
                    })
                
                metadata['status'] = "✅ Metrics Loaded"
    except Exception as e:
        pass
    
    return metadata

@st.cache_resource
def load_model():
    """Load the trained model from artifacts directory."""
    try:
        project_root = Path(__file__).parent.parent
        model_path = project_root / "artifacts" / "model.joblib"
        
        if model_path.exists():
            model = joblib.load(model_path)
            return model
        else:
            return None
    except Exception as e:
        st.warning(f"⚠️ Could not load model: {str(e)}")
        return None

# ===========================
# LOAD DATA
# ===========================
with st.spinner('🔄 Loading air quality data...'):
    historical_df = load_historical_data()
    model_metadata = get_model_metadata()
    model = load_model()

# Get recent data (last 7 days) - MUST BE BEFORE SIDEBAR
recent_df = historical_df.tail(24 * 7)
latest_data = historical_df.iloc[-1]

# Calculate data freshness - MUST BE BEFORE SIDEBAR
latest_ts = pd.to_datetime(latest_data['timestamp'])
now_aware = datetime.now(timezone.utc) if latest_ts.tzinfo else datetime.now()
data_age_hours = (now_aware - latest_ts).total_seconds() / 3600

# ===========================
# SIDEBAR: CI/CD PIPELINE STATUS
# ===========================
with st.sidebar:
    st.markdown("### 🔄 Pipeline Status")
    st.markdown("---")
    
    st.markdown("**📊 Data Ingestion**")
    st.caption("Runs: Hourly")
    latest_timestamp = pd.to_datetime(historical_df['timestamp'].iloc[-1])
    now_aware_check = datetime.now(timezone.utc) if latest_timestamp.tzinfo else datetime.now()
    time_since_update = (now_aware_check - latest_timestamp).total_seconds() / 3600
    
    if time_since_update < 2:
        st.success("Active", icon="✅")
    elif time_since_update < 6:
        st.warning(f"⚠️ {time_since_update:.1f}h ago", icon="⚠️")
    else:
        st.error(f"❌ {time_since_update:.1f}h ago", icon="❌")
    
    st.markdown("**🤖 Training Pipeline**")
    st.caption("Runs: Daily @ 8:00 AM")
    st.info("Scheduled", icon="📊")
    
    st.markdown("**🎯 Active Model**")
    if model is not None:
        st.success(f"{model_metadata['best_model']}", icon="✅")
        st.caption(f"Status: {model_metadata['status']}")
        st.markdown("**Performance Metrics:**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("MAE", f"{model_metadata['mae']:.2f}")
            st.metric("R²", f"{model_metadata['r2']:.4f}")
        with col2:
            st.metric("RMSE", f"{model_metadata['rmse']:.2f}")
    else:
        st.error("❌ Model not loaded", icon="❌")
    
    st.markdown("---")
    
    st.markdown("**📅 Data Information**")
    st.caption(f"Updated: {latest_data['timestamp'].strftime('%b %d, %I:%M %p')}")
    st.caption(f"Age: {data_age_hours:.1f}h")
    st.caption(f"Total Records: {len(historical_df)}")
    st.caption(f"7-Day Average: {recent_df['aqi'].mean():.0f}")
    
    st.markdown("---")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()

# Handle future timestamps (timezone bug)
if data_age_hours < -1:
    data_freshness_icon = "🚨"
    data_freshness_text = f"Sync issue ({abs(data_age_hours):.1f}h)"
elif data_age_hours < 0:
    data_freshness_icon = "✅"
    data_freshness_text = "Just updated"
elif data_age_hours > 2:
    data_freshness_icon = "⚠️"
    data_freshness_text = f"Updated {data_age_hours:.1f}h ago"
else:
    data_freshness_icon = "✅"
    data_freshness_text = f"Updated {data_age_hours:.1f}h ago"

# ===========================
# HEADER
# ===========================
st.markdown(f"""
<div class="hero-header">
    <h1 class="hero-title">🌫️ Karachi AQI Predictor</h1>
    <p class="hero-subtitle">Real-Time Air Quality Monitoring & ML-Powered Forecasting</p>
    <div class="status-info">
        <span>📅 {latest_data['timestamp'].strftime('%B %d, %Y')}</span>
        <span>🕐 {latest_data['timestamp'].strftime('%I:%M %p')}</span>
        <span>{data_freshness_icon} {data_freshness_text}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ===========================
# KEY METRICS
# ===========================
current_aqi = latest_data['aqi']
current_category, current_color = get_aqi_category_info(current_aqi)
avg_24h = recent_df.tail(24)['aqi'].mean()
avg_category, avg_color = get_aqi_category_info(avg_24h)
max_7d = recent_df['aqi'].max()
max_category, max_color = get_aqi_category_info(max_7d)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Current AQI</div>
        <div class="metric-value" style='color: {current_color};'>{current_aqi:.0f}</div>
        <div class="metric-desc" style='color: {current_color};'>{current_category}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">24-Hour Avg</div>
        <div class="metric-value" style='color: {avg_color};'>{avg_24h:.0f}</div>
        <div class="metric-desc" style='color: {avg_color};'>{avg_category}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">7-Day Peak</div>
        <div class="metric-value" style='color: {max_color};'>{max_7d:.0f}</div>
        <div class="metric-desc" style='color: {max_color};'>{max_category}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    unhealthy_hours = len(recent_df[recent_df['aqi'] > 150])
    if unhealthy_hours == 0:
        alert_icon, alert_text, alert_color = "✅", "All Clear", "#28a745"
    elif unhealthy_hours <= 24:
        alert_icon, alert_text, alert_color = "⚠️", f"{unhealthy_hours}h Alert", "#f39c12"
    else:
        alert_icon, alert_text, alert_color = "🚨", f"{unhealthy_hours}h Critical", "#e74c3c"
    
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">Health Alert</div>
        <div style='font-size: 2.5rem; margin: 0.5rem 0;'>{alert_icon}</div>
        <div class="metric-desc" style='color: {alert_color};'>{alert_text}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# HEALTH ALERT BANNER
# ===========================
if current_aqi > 150:
    st.markdown(f"""
    <div class='alert-box'>
        <div style='font-size: 1.8rem; margin-bottom: 0.5rem; font-weight: 700;'>🚨 Air Quality Health Alert</div>
        <div style='font-size: 1.1rem; margin-bottom: 0.5rem;'>Current AQI: {current_aqi:.0f} - {current_category}</div>
        <div style='margin-top: 0.5rem; font-size: 0.95rem; line-height: 1.5;'>{get_health_recommendation(current_aqi)}</div>
    </div>
    """, unsafe_allow_html=True)
elif current_aqi > 100:
    st.markdown(f"""
    <div class='warning-box'>
        <div style='font-size: 1.5rem; margin-bottom: 0.3rem; font-weight: 700;'>⚠️ Air Quality Advisory</div>
        <div style='font-size: 1rem; margin-bottom: 0.5rem;'>Current AQI: {current_aqi:.0f} - {current_category}</div>
        <div style='margin-top: 0.5rem; font-size: 0.9rem; line-height: 1.5;'>{get_health_recommendation(current_aqi)}</div>
    </div>
    """, unsafe_allow_html=True)

# ===========================
# 3-DAY FORECAST
# ===========================
st.markdown("<div class='section-header'>🔮 3-Day Forecast</div>", unsafe_allow_html=True)

if model is not None:
    st.info(f"📊 Predictions from {model_metadata['best_model']} (MAE: {model_metadata['mae']:.2f}) — Recursive multi-step forecasting")

st.markdown("<br>", unsafe_allow_html=True)

if model is not None:
    # ✅ This now calls utils.generate_forecast() which uses the correct
    #    recursive logic with aqi_lag_1, aqi_lag_24, aqi_lag_48 features
    #    that match what the model was actually trained on.
    forecast_df = generate_forecast(historical_df, model, days=3)
    
    if forecast_df is not None and not forecast_df.empty:
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            # Combine historical (last 7 days) and forecast
            recent_history = historical_df.tail(24 * 7)[['timestamp', 'aqi']].copy()
            recent_history['type'] = 'Historical'
            recent_history.rename(columns={'aqi': 'value'}, inplace=True)
            
            forecast_plot = forecast_df.copy()
            forecast_plot['type'] = 'Forecast'
            forecast_plot.rename(columns={'aqi_predicted': 'value'}, inplace=True)
            
            combined = pd.concat([recent_history, forecast_plot], ignore_index=True)
            
            fig = px.line(combined, x='timestamp', y='value', color='type',
                         title='AQI Trend: Historical + 3-Day Forecast',
                         labels={'value': 'AQI', 'timestamp': 'Date & Time'},
                         color_discrete_map={'Historical': '#667eea', 'Forecast': '#f39c12'})
            
            fig.add_hline(y=50, line_dash="dash", line_color="green", opacity=0.3,
                         annotation_text="Good")
            fig.add_hline(y=100, line_dash="dash", line_color="yellow", opacity=0.3,
                         annotation_text="Moderate")
            fig.add_hline(y=150, line_dash="dash", line_color="orange", opacity=0.3,
                         annotation_text="Unhealthy")
            
            fig.update_layout(
                height=400, 
                hovermode='x unified',
                plot_bgcolor='rgba(37, 45, 61, 0.5)',
                paper_bgcolor='#1a1f2e',
                font=dict(color='#e0e0e0'),
                xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(102, 126, 234, 0.2)'),
                yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(102, 126, 234, 0.2)')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.markdown("#### 📅 Next 3 Days")
            
            for day in range(1, 4):
                day_start = day - 1
                day_data = forecast_df.iloc[day_start * 24:(day_start + 1) * 24]
                avg_aqi = day_data['aqi_predicted'].mean()
                max_aqi = day_data['aqi_predicted'].max()
                min_aqi = day_data['aqi_predicted'].min()
                
                category, color = get_aqi_category_info(avg_aqi)
                today = datetime.now()
                forecast_date = (today + timedelta(days=day)).strftime('%b %d')
                
                st.markdown(f"""
                <div class='forecast-card' style='border-left-color: {color};'>
                    <div style='font-weight: 600; font-size: 0.85rem; color: #666; margin-bottom: 0.5rem;'>
                        {forecast_date} (Day {day})
                    </div>
                    <div style='font-size: 2rem; font-weight: 700; color: {color}; margin: 0.3rem 0;'>{avg_aqi:.0f}</div>
                    <div style='font-size: 0.9rem; color: {color}; font-weight: 600; margin-bottom: 0.5rem;'>{category}</div>
                    <div style='font-size: 0.8rem; color: #888;'>Range: {min_aqi:.0f} - {max_aqi:.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.caption(f"Model: {model_metadata['best_model']} | Recursive forecasting")
    else:
        st.warning("⚠️ Forecast returned empty. Check that historical_df has an 'aqi' column and at least 49 rows.")
else:
    st.warning("⚠️ Prediction model not available. Please train the model first.")
    st.info("💡 Run: `python -m src.Pipeline.train_daily` to train the model.")

st.markdown("<br>", unsafe_allow_html=True)

# ===========================
# HEALTH RECOMMENDATIONS
# ===========================
st.markdown("<div class='section-header'>💡 Health Recommendations</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

recommendation = get_health_recommendation(current_aqi)
if current_aqi <= 50:
    st.success(f"✅ {recommendation}")
elif current_aqi <= 100:
    st.info(f"ℹ️ {recommendation}")
elif current_aqi <= 150:
    st.warning(f"⚠️ {recommendation}")
else:
    st.error(f"🚨 {recommendation}")

st.divider()

# ===========================
# DETAILED ANALYTICS (TABS)
# ===========================
st.markdown("<div class='section-header'>📊 Detailed Analytics & Insights</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📈 Historical Trends", "🧪 Pollutant Analysis"])

with tab1:
    st.markdown("#### Past 7 Days Air Quality Trend")
    
    fig_hist = go.Figure()
    
    fig_hist.add_trace(go.Scatter(
        x=recent_df['timestamp'],
        y=recent_df['aqi'],
        mode='lines',
        name='AQI',
        line=dict(color='#667eea', width=2.5),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)',
        hovertemplate='<b>%{x|%b %d, %I:%M %p}</b><br>AQI: %{y:.0f}<extra></extra>'
    ))
    
    fig_hist.add_hline(y=50, line_dash="dash", line_color="green", opacity=0.5, annotation_text="Good")
    fig_hist.add_hline(y=100, line_dash="dash", line_color="yellow", opacity=0.5, annotation_text="Moderate")
    fig_hist.add_hline(y=150, line_dash="dash", line_color="orange", opacity=0.5, annotation_text="Unhealthy")
    
    fig_hist.update_layout(
        title="Past 7 Days Air Quality Trend",
        xaxis_title="Date",
        yaxis_title="Air Quality Index (AQI)",
        height=450,
        hovermode='x unified',
        plot_bgcolor='rgba(37, 45, 61, 0.5)',
        paper_bgcolor='#1a1f2e',
        font=dict(color='#e0e0e0'),
        showlegend=False
    )
    
    fig_hist.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(102, 126, 234, 0.2)')
    fig_hist.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(102, 126, 234, 0.2)')
    
    st.plotly_chart(fig_hist, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Weekly Average", f"{recent_df['aqi'].mean():.0f}")
    with col2:
        st.metric("📈 Peak This Week", f"{recent_df['aqi'].max():.0f}")
    with col3:
        st.metric("📉 Best This Week", f"{recent_df['aqi'].min():.0f}")

with tab2:
    st.markdown("#### Current Pollutant Breakdown")
    
    pollutants = {
        "PM2.5": "pm2_5",
        "PM10": "pm10",
        "CO": "carbon_monoxide",
        "NO₂": "nitrogen_dioxide",
        "SO₂": "sulphur_dioxide",
        "O₃": "ozone"
    }
    
    pollutant_data = []
    for name, col in pollutants.items():
        if col in latest_data.index and pd.notna(latest_data[col]):
            try:
                pollutant_data.append({"Pollutant": name, "Concentration": float(latest_data[col])})
            except (ValueError, TypeError):
                pass
    
    if pollutant_data:
        pollutant_df = pd.DataFrame(pollutant_data)
        
        fig_pollutants = px.bar(
            pollutant_df,
            x="Pollutant",
            y="Concentration",
            title="Current Pollutant Concentrations (μg/m³)",
            color="Concentration",
            color_continuous_scale=["#28a745", "#ffc107", "#dc3545"],
            text="Concentration"
        )
        
        fig_pollutants.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_pollutants.update_layout(
            height=400, 
            showlegend=False,
            plot_bgcolor='rgba(37, 45, 61, 0.5)',
            paper_bgcolor='#1a1f2e',
            font=dict(color='#e0e0e0'),
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(102, 126, 234, 0.2)'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(102, 126, 234, 0.2)')
        )
        
        st.plotly_chart(fig_pollutants, use_container_width=True)
        
        st.info("""
        **📌 Pollutant Guide:**
        - **PM2.5 & PM10**: Particulate matter - main AQI contributor
        - **CO**: Carbon monoxide from vehicles
        - **NO₂**: Nitrogen dioxide from traffic and industry
        - **SO₂**: Sulfur dioxide from fossil fuels
        - **O₃**: Ozone from sunlight reacting with pollutants
        """)
    else:
        st.info("📊 Pollutant data not available in current dataset")


st.divider()

# ===========================
# AQI GUIDE SECTION
# ===========================
st.markdown("<div class='section-header'>📖 AQI Guide</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 🟢 Good (0–50)
    Air quality is excellent — perfect for all outdoor activities.

    #### 🟡 Moderate (51–100)
    Air quality is acceptable — safe for most people.

    #### 🟠 Unhealthy for Sensitive Groups (101–150)
    Sensitive groups should limit prolonged outdoor exposure.
    """)

with col2:
    st.markdown("""
    #### 🔴 Unhealthy (151–200)
    Everyone should reduce prolonged outdoor activities.

    #### 🟣 Very Unhealthy (201–300)
    Health alert — avoid outdoor activities.

    #### 🟤 Hazardous (301+)
    Emergency conditions — stay indoors.
    """)

st.divider()

# ===========================
# MODEL INFO SECTION
# ===========================
st.markdown("<div class='section-header'>🤖 Model Info</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"""
    <div style='background: #252d3d; padding: 1.5rem; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.4); border: 1px solid rgba(102, 126, 234, 0.3);'>
        <h4 style="color: #e0e0e0;">📊 Active Model: {model_metadata['best_model']}</h4>
        <p style="color: #c0c0c0;"><strong>Status:</strong> {model_metadata['status']}</p>
        <p style="color: #c0c0c0;"><strong>Performance Metrics:</strong></p>
        <ul style="color: #c0c0c0;">
            <li><strong>MAE:</strong> {model_metadata['mae']:.4f} AQI points (mean absolute error)</li>
            <li><strong>RMSE:</strong> {model_metadata['rmse']:.4f} (root mean squared error)</li>
            <li><strong>R² Score:</strong> {model_metadata['r2']:.4f} (prediction accuracy)</li>
        </ul>
        <p style='margin-top: 1rem; color: #10b981;'><strong>✅ High-performance model trained on Karachi air quality data</strong></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.info("""
    **🔬 Model Insights**

    📓 **SHAP Analysis**
    `notebooks/shap_analysis.ipynb`

    Understand:
    - Feature importance
    - Model decisions
    - Prediction breakdown
    """)

st.markdown("#### 🏆 Model Comparison")

metrics_data = {
    "Model": ["LinearRegression", "RandomForest", "GradientBoosting"],
    "MAE": [6.9263, 6.9418, 6.5196],
    "RMSE": [10.7103, 10.2606, 9.7755],
    "R²": [0.8809, 0.8907, 0.9008]

}
metrics_df = pd.DataFrame(metrics_data)

def highlight_best(row):
    if row["Model"] == "GradientBoosting":
        return ['background-color: #667eea; color: white;'] * len(row)
    return ['color: #e0e0e0;'] * len(row)

st.dataframe(
    metrics_df.style.apply(highlight_best, axis=1)
                    .format({"MAE": "{:.4f}", "RMSE": "{:.4f}", "R²": "{:.4f}"}),
    use_container_width=True,
    hide_index=True
)

st.success("✅ **Best Model: GradientBoosting** (Lowest MAE & RMSE, Highest R²)")
st.caption("**Training data:** 8870 samples | **Features:** 7 (aqi lags + temporal features)")

st.divider()

# ===========================
# FOOTER
# ===========================
st.markdown("""
<div style='text-align: center; padding: 2rem 0; color: #808080; border-top: 1px solid #3a4250; margin-top: 2rem;'>
    <p style='font-size: 0.9rem;'>🌍 <strong style="color: #e0e0e0;">Karachi AQI Predictor</strong> | Built with Streamlit + Hopsworks + GradientBoosting</p>
    <p style='font-size: 0.8rem; color: #606060;'>Data updates hourly | Models retrain daily | Predictions refresh every 30 minutes</p>
</div>
""", unsafe_allow_html=True)