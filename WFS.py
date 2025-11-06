import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pytz
import collections
import streamlit as st
import pandas as pd

load_dotenv()

# --- UI Setup ---
st.set_page_config(
    page_title="Adani Natural Resources | Weather Intelligence Mining",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.3rem;
        font-weight: bold;
        color: #04386f;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #18964d;
        text-align: center;
        margin-bottom: 2rem;
    }
    .mine-name {
        font-size: 1.1rem;
        font-weight: bold;
        color: #071654;
        margin-top: 1.2rem;
        margin-bottom: 0.6rem;
    }
    .metric-card {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-high {
        background-color: #fde0e6;
        border-left: 5px solid #f44336;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #7a0101;
        font-weight: 600;
    }
    .alert-moderate {
        background-color: #fff4de;
        border-left: 5px solid #ffa500;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #7c4106;
        font-weight: 600;
    }
    .alert-low {
        background-color: #e0f4e7;
        border-left: 5px solid #07b34f;
        padding: 1rem;
        margin: 0.5rem 0;
        color: #074124 !important;
        font-weight: 600;
    }
    .slab-card {
        background-color: #f7fcfe;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
        font-size: 0.98rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- API Keys and Mine Locations (with requested names) ---
OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENMETEO_KEY = os.getenv("OPENMETEO_API_KEY")
TOMORROWIO_KEY = os.getenv("TOMORROW_API_KEY")
ACCUWEATHER_KEY = os.getenv("ACCUWEATHER_API_KEY")

MINE_LOCATIONS = [
    {"name": "Suliyari", "lat": float(os.getenv("LAT1")), "lon": float(os.getenv("LON1")), "accuweather_location_key": os.getenv("LOCATION_KEY1")},
    {"name": "PKEB", "lat": float(os.getenv("LAT2")), "lon": float(os.getenv("LON2")), "accuweather_location_key": os.getenv("LOCATION_KEY2")},
    {"name": "Talabira", "lat": float(os.getenv("LAT3")), "lon": float(os.getenv("LON3")), "accuweather_location_key": os.getenv("LOCATION_KEY3")},
    {"name": "GPIII", "lat": float(os.getenv("LAT4")), "lon": float(os.getenv("LON4")), "accuweather_location_key": os.getenv("LOCATION_KEY4")},
    {"name": "Kurmitar", "lat": float(os.getenv("LAT5")), "lon": float(os.getenv("LON5")), "accuweather_location_key": os.getenv("LOCATION_KEY5")},
]

# --- Timezone and alert settings ---
IST = pytz.timezone('Asia/Kolkata')
UTC = pytz.utc
REQUEST_TIMEOUT = 10

WIND_ALERT_THRESHOLD_KMH = 30
VISIBILITY_ALERT_THRESHOLD_KM = 1.0
MIN_RAINFALL_FOR_SLAB_DISPLAY_MM = 0.6
MAX_SLABS_TO_SHOW = 6

# --- Helpers, API Calls, and Forecast Logic... ---
# (Keep the rest of your forecast/aggregation functions as in the previous script,
# no changes needed there for UI/label improvements)

# --- Streamlit Main ---
st.markdown('<div class="main-header">Adani Natural Resources</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Weather Intelligence – Mining</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Mines")
    mine_names = [mine["name"] for mine in MINE_LOCATIONS]
    selected_mines = st.multiselect("Select Mine", mine_names, default=mine_names)
    st.markdown("---")
    st.info("Data from OpenWeatherMap, Open-Meteo, Tomorrow.io, and AccuWeather APIs.")

if not selected_mines:
    st.warning("Please select at least one mine to view the dashboard.")
    st.stop()

# ...Place all your forecast-by-mine code blocks here,
# using st.markdown(alerts) as in the previous script,
# but with slightly improved messaging/colors above.


# (example for low impact status:)
# st.markdown('<div class="alert-low"><strong>✅ Low Impact:</strong> Normal operations, minor impact possible.</div>', unsafe_allow_html=True)

# (Call and display your metrics, slabs, and status like before) 

# --- END ---

