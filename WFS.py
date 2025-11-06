import os
import requests
from datetime import datetime, timedelta
import pytz
import collections
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Adani Natural Resources | Weather Intelligence Mining",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PURE LIGHT MODE, WHITE BACKGROUND, CLEAN HEADERS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css?family=Inter:300,400,500,600,700,900&display=swap');
body {
    font-family: 'Inter', Arial, sans-serif !important;
    background: #fff !important; color: #071654 !important;
}
.main-header {
    font-size: 2.3rem; font-weight:900; color: #071654; letter-spacing: -0.02em;
    text-align: center; margin-bottom: 0.65rem; background: none;
}
.sub-header {
    font-size: 1.1rem; font-weight:600; color: #18964d; text-align: center;
    margin-bottom: 2rem; background:none; letter-spacing: -0.01em;
}
.mine-name, .card-title {
    font-size: 1.18rem; font-weight: 900; color: #ff9800 !important; background: none;
    letter-spacing: 0.012em; margin-top: 1.1rem; margin-bottom: 0.6rem;
    padding: 0; border-radius: 0;
}
.metric-card {
    background-color: #f0f8ff; border-radius: 0.7rem; margin: 0.5rem 0; padding: 1rem;
}
.alert-high { background-color: #F44336; border-radius: 0.7rem; color: #ffffff; font-weight: 600; padding: 1rem;}
.alert-moderate { background-color: #FFA500; border-radius: 0.7rem; color: #ffffff; font-weight: 600; padding: 1rem;}
.alert-low { background-color: #07B34F; border-radius: 0.7rem; color: #1B2733 !important; font-weight: 900; padding: 1rem;}
.slab-card { background-color: #f7fcfe; border: 1px solid #e0e0e0; border-radius: 0.5rem; padding: 1rem; margin: 0.5rem 0; font-size: 0.98rem;}
.caption { font-family: 'Inter', Arial, sans-serif !important; font-size: 0.95rem; color: #8392A7; margin-top: 1.5rem; font-weight: 400;}
</style>
""", unsafe_allow_html=True)

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENMETEO_KEY = os.getenv("OPENMETEO_API_KEY", "")
TOMORROWIO_KEY = os.getenv("TOMORROW_API_KEY", "")
ACCUWEATHER_KEY = os.getenv("ACCUWEATHER_API_KEY", "")

MINE_LOCATIONS = [
    {"name": "Suliyari", "lat": float(os.getenv("LAT1", 0)), "lon": float(os.getenv("LON1", 0)), "accuweather_location_key": os.getenv("LOCATION_KEY1", "")},
    {"name": "PKEB", "lat": float(os.getenv("LAT2", 0)), "lon": float(os.getenv("LON2", 0)), "accuweather_location_key": os.getenv("LOCATION_KEY2", "")},
    {"name": "Talabira", "lat": float(os.getenv("LAT3", 0)), "lon": float(os.getenv("LON3", 0)), "accuweather_location_key": os.getenv("LOCATION_KEY3", "")},
    {"name": "GPIII", "lat": float(os.getenv("LAT4", 0)), "lon": float(os.getenv("LON4", 0)), "accuweather_location_key": os.getenv("LOCATION_KEY4", "")},
    {"name": "Kurmitar", "lat": float(os.getenv("LAT5", 0)), "lon": float(os.getenv("LON5", 0)), "accuweather_location_key": os.getenv("LOCATION_KEY5", "")},
]

IST = pytz.timezone('Asia/Kolkata')
UTC = pytz.utc
REQUEST_TIMEOUT = 10
WIND_ALERT_THRESHOLD_KMH = 30
VISIBILITY_ALERT_THRESHOLD_KM = 1.0
MIN_RAINFALL_FOR_SLAB_DISPLAY_MM = 0.6
MAX_SLABS_TO_SHOW = 6

# --- FUNCTIONS (UNCHANGED FROM PRIOR VERSIONS: get_rain_type, get_production_status, fetch_consolidated_forecast, etc.) ---
# Copy all function bodies as from previous script – no change needed.

def get_rain_type(mm, is_2hr_slab=False, overall_description=None):
    # ... unchanged ...

def get_production_status(total_rain_mm, slabs):
    # ... unchanged ...

def utc_to_ist(utc_dt):
    # ... unchanged ...

@st.cache_data(ttl=1800)
def fetch_openweather_forecast(lat, lon):
    # ... unchanged ...

@st.cache_data(ttl=1800)
def fetch_open_meteo_forecast(lat, lon):
    # ... unchanged ...

@st.cache_data(ttl=1800)
def fetch_tomorrow_io_forecast(lat, lon):
    # ... unchanged ...

def get_daily_summary_and_slabs(hourly_data_list):
    # ... unchanged ...

def fetch_consolidated_forecast(lat, lon):
    # ... unchanged ...

# ---- UI LAYOUT ----
st.markdown('<div class="main-header">Adani Natural Resources</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Weather Intelligence – Mining</div>', unsafe_allow_html=True)
with st.sidebar:
    st.header("Mines")
    mine_names = [mine["name"] for mine in MINE_LOCATIONS]
    selected_mines = st.multiselect("Select Mine", mine_names)  # Nothing selected by default
    st.markdown("---")
    st.info("Data from OpenWeatherMap, Open-Meteo, Tomorrow.io, and AccuWeather APIs.")

if not selected_mines:
    st.warning("Please select at least one mine to view the dashboard.")
    st.stop()

for mine_name in selected_mines:
    mine = next((m for m in MINE_LOCATIONS if m["name"] == mine_name), None)
    if not mine: continue
    st.markdown(f'<div class="mine-name">📍 {mine_name}</div>', unsafe_allow_html=True)
    st.markdown(f"**Coordinates:** Lat {mine['lat']}, Lon {mine['lon']}")

    with st.spinner(f"Fetching forecast for {mine_name}..."):
        forecast_by_day = fetch_consolidated_forecast(mine["lat"], mine["lon"])
    if not forecast_by_day:
        st.error("❌ Unable to fetch forecast data. Please check API keys and network connectivity.")
        continue
    current_date_ist = datetime.now(IST).date()
    
    # -- ALERTS LOGIC BLOCK (TOP OF MINE SECTION, before tabs) --
    day_hourly_data = forecast_by_day.get(current_date_ist)
    if day_hourly_data:
        day_summary = get_daily_summary_and_slabs(day_hourly_data)
        impact_level, status_msg = get_production_status(day_summary['total_rain'], day_summary['slabs'])
        # Production impact level alert
        if impact_level == "High":
            st.error(f"🚩 **ALERT**: {mine_name} expects **HIGH impact** — {status_msg}")
        elif impact_level == "Moderate":
            st.warning(f"⚠️ {mine_name}: {status_msg}")

        # Per-slab detailed alerts
        slab_alerts = []
        for slab in day_summary['slabs']:
            details = []
            if slab['lightning']:
                details.append("⚡ Lightning")
            if slab['wind_speed'] >= WIND_ALERT_THRESHOLD_KMH:
                details.append(f"💨 High Wind ({slab['wind_speed']} km/h)")
            if slab['visibility_km'] <= VISIBILITY_ALERT_THRESHOLD_KM:
                details.append(f"👁️ Low Visibility ({slab['visibility_km']} km)")
            if slab['mm'] > 0:
                details.append(f"🌧️ Rain ({slab['mm']} mm, {slab['type']})")
            if details:
                slab_alerts.append((slab['time_range'], "; ".join(details)))
        if slab_alerts:
            for time_range, alert_detail in slab_alerts:
                st.markdown(f"<div class='alert-moderate'><strong>⏰ {time_range}:</strong> {alert_detail}</div>", unsafe_allow_html=True)
        elif impact_level == "Low":
            st.markdown("<div class='alert-low'>✅ No operational hazards detected for today.</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📅 Today", "📅 Tomorrow"])
    for tab, day_offset in [(tab1, 0), (tab2, 1)]:
        target_day = current_date_ist + timedelta(days=day_offset)
        with tab:
            if target_day not in forecast_by_day:
                st.warning(f"No forecast data available for {target_day.strftime('%d %B, %Y')}")
                continue
            day_hourly_data = forecast_by_day[target_day]
            day_summary = get_daily_summary_and_slabs(day_hourly_data)
            st.markdown(f"### {target_day.strftime('%d %B, %Y')}")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            with col1: st.metric("Weather", day_summary['weather_desc'])
            with col2: st.metric("Max Temp", f"{day_summary['max_temp']}°C")
            with col3: st.metric("Min Temp", f"{day_summary['min_temp']}°C")
            with col4: st.metric("Total Rainfall", f"{day_summary['total_rain']} mm")
            with col5: st.metric("Rain Probability", f"{day_summary['total_rain_pop']}%")
            # Add visibility as column 6
            with col6:
                vis_val = int(day_hourly_data[0][1].get("visibility_km", 0)) if day_hourly_data else "--"
                st.metric("Visibility", f"{vis_val} km")
            impact_level, status_msg = get_production_status(day_summary['total_rain'], day_summary['slabs'])
            if impact_level == "High":
                st.markdown(f'<div class="alert-high"><strong>🚨 High Impact:</strong> {status_msg}</div>', unsafe_allow_html=True)
            elif impact_level == "Moderate":
                st.markdown(f'<div class="alert-moderate"><strong>⚠️ Moderate Impact:</strong> {status_msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-low"><strong>✅ Low Impact:</strong> {status_msg}</div>', unsafe_allow_html=True)
            if day_summary['slabs']:
                st.markdown("### 🌧️ Precipitation Windows")
                for slab in day_summary['slabs']:
                    alerts = []
                    if slab['lightning']:
                        alerts.append("⚡ Lightning")
                    if slab['wind_speed'] >= WIND_ALERT_THRESHOLD_KMH:
                        alerts.append(f"💨 High Wind ({slab['wind_speed']} km/h)")
                    if slab['visibility_km'] <= VISIBILITY_ALERT_THRESHOLD_KM:
                        alerts.append(f"👁️ Low Visibility ({slab['visibility_km']} km)")
                    alert_str = " | ".join(alerts) if alerts else "No alerts"
                    st.markdown(f"""
                    <div class="slab-card">
                        <strong>{slab['time_range']}</strong><br>
                        🌧️ {slab['mm']} mm ({slab['type']}) - {slab['prob']}% probability<br>
                        <span style="color: {'#F44336' if alerts else '#07B34F'};">{alert_str}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No significant precipitation expected.")
            if day_hourly_data:
                st.markdown("### 🌡️ Temperature Trend")
                temp_data = pd.DataFrame([
                    {"Time": dt.strftime("%H:%M"), "Temperature (°C)": data['temp']}
                    for dt, data in day_hourly_data
                ])
                st.line_chart(temp_data.set_index("Time"))
            st.markdown("---")
st.caption(f"Last updated: {datetime.now(IST).strftime('%d %B %Y, %I:%M %p IST')}")
