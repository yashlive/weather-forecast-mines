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

# --- Theme switcher ---
with st.sidebar:
    mode = st.radio("Theme", ["🌞 Light mode", "🌙 Dark mode"], index=0)

LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css?family=Inter:300,400,500,600,700,900&display=swap');
body {
    font-family: 'Inter', Arial, sans-serif !important;
    background: #FAFBFF !important; color: #071654 !important;
}
.main-header {
    font-size: 2.3rem; font-weight:900; color: #071654; letter-spacing: -0.02em;
    text-align: center; margin-bottom: 0.65rem; background: none; border-radius: 0; box-shadow:none; padding-top:.6rem; padding-bottom:.18rem;
}
.sub-header {
    font-size: 1.1rem; font-weight:600; color: #18964d; text-align: center;
    margin-bottom: 2rem; background:none; border-radius:0; padding: .13rem 0 0.1rem 0;
    letter-spacing: -0.01em;
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
"""

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css?family=Inter:300,400,500,600,700,900&display=swap');
body {
    font-family: 'Inter', Arial, sans-serif !important;
    background: #181c24 !important; color: #ffd86a !important;
}
.main-header {
    font-size: 2.3rem; font-weight:900; color: #ffd86a; letter-spacing: -0.02em;
    text-align: center; margin-bottom: 0.65rem; background: none; border-radius: 0; box-shadow:none; padding-top:.6rem; padding-bottom:.18rem;
}
.sub-header {
    font-size: 1.1rem; font-weight:600; color: #57d0ff; text-align: center;
    margin-bottom: 2rem; background:none; border-radius:0; padding: .13rem 0 0.1rem 0;
    letter-spacing: -0.01em;
}
.mine-name, .card-title {
    font-size: 1.18rem; font-weight: 900; color: #ffc400 !important; background: none;
    letter-spacing: 0.012em; margin-top: 1.1rem; margin-bottom: 0.6rem;
    padding: 0; border-radius: 0;
}
.metric-card {
    background-color: #23242a; border-radius: 0.7rem; margin: 0.5rem 0; padding: 1rem; color: #fbead7;
}
.alert-high { background-color: #e53935; border-radius: 0.7rem; color: #fffefe; font-weight: 600; padding: 1rem;}
.alert-moderate { background-color: #ff9000; border-radius: 0.7rem; color: #fff; font-weight: 600; padding: 1rem;}
.alert-low { background-color: #57e39d; border-radius: 0.7rem; color: #181c24 !important; font-weight: 900; padding: 1rem;}
.slab-card { background-color: #161928; border: 1px solid #2d3649; border-radius: 0.5rem; padding: 1rem; margin: 0.5rem 0; color: #fff3; font-size: 0.98rem;}
.caption { font-family: 'Inter', Arial, sans-serif !important; font-size: 0.95rem; color: #ababab; margin-top: 1.5rem; font-weight: 400;}
</style>
"""

if mode == "🌙 Dark mode":
    st.markdown(DARK_CSS, unsafe_allow_html=True)
else:
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)

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

def get_rain_type(mm, is_2hr_slab=False, overall_description=None):
    if is_2hr_slab:
        if mm >= 8: return "very heavy rain (torrential)"
        elif mm >= 5: return "heavy rain"
        elif mm >= 1.5: return "moderate rain"
        elif mm >= 0.3: return "light rain"
        elif mm > 0: return "drizzle"
        else: return "no rain"
    else:
        if mm >= 25: return "Very Heavy Rain & Storm ⛈️"
        elif mm >= 15: return "Heavy Rain 🌧️"
        elif mm >= 5: return "Moderate Rain ☔"
        elif mm >= 1: return "Light Rain 🌦️"
        elif mm > 0: return "Drizzle 💧"
        else:
            if overall_description:
                desc_lower = overall_description.lower()
                if "clear" in desc_lower or "sun" in desc_lower: return "Sunny ☀️"
                elif "cloud" in desc_lower or "overcast" in desc_lower: return "Cloudy ☁️"
                elif "fog" in desc_lower or "mist" in desc_lower: return "Foggy 🌫️"
                elif "thunderstorm" in desc_lower or "storm" in desc_lower: return "Thunderstorm ⚡"
                elif "rain" in desc_lower: return "Rainy ☔"
            return "No Rain ☀️"

def get_production_status(total_rain_mm, slabs):
    # If absolutely NO rain/precip etc, and NO alert slabs, show totally clear status
    no_rain = (total_rain_mm == 0)
    no_alerts = True
    for slab in slabs:
        if slab['mm'] > 0 or slab['lightning'] or slab['wind_speed'] >= WIND_ALERT_THRESHOLD_KMH or slab['visibility_km'] <= VISIBILITY_ALERT_THRESHOLD_KM:
            no_alerts = False
            break
    if no_rain and no_alerts:
        return "Low", "Clear weather. No operational hazard."
    impact_level = "Low"
    status_msg = "Normal operations, minor impact possible"
    if total_rain_mm >= 15:
        impact_level = "High"
        status_msg = "Production may be significantly impacted due to heavy rainfall."
    elif total_rain_mm >= 5:
        impact_level = "Moderate"
        status_msg = "Proceed with caution, production may be impacted due to moderate rainfall."
    has_lightning, has_high_wind, has_low_visibility = False, False, False
    for slab in slabs:
        if slab['lightning']: has_lightning = True
        if slab['wind_speed'] >= WIND_ALERT_THRESHOLD_KMH: has_high_wind = True
        if slab['visibility_km'] <= VISIBILITY_ALERT_THRESHOLD_KM: has_low_visibility = True
    if has_lightning:
        if impact_level != "High":
            impact_level = "High"
            status_msg = "Blasting/open-pit operations likely impacted due to lightning."
        else:
            status_msg += " Additionally, lightning expected."
    if has_high_wind:
        if impact_level == "Low":
            impact_level = "Moderate"
            status_msg = "Caution advised due to high winds, potential dust/equipment issues."
        elif "wind" not in status_msg.lower():
            status_msg += " High winds also expected."
    if has_low_visibility:
        if impact_level == "Low":
            impact_level = "Moderate"
            status_msg = "Caution advised due to low visibility, impacting vehicle movement."
        elif "visibility" not in status_msg.lower():
            status_msg += " Low visibility also expected."
    return (impact_level, status_msg)

def utc_to_ist(utc_dt):
    if utc_dt.tzinfo is None:
        utc_dt = UTC.localize(utc_dt)
    return utc_dt.astimezone(IST)

@st.cache_data(ttl=1800)
def fetch_openweather_forecast(lat, lon):
    if not OPENWEATHER_KEY: return None
    try:
        url = (f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}"
               f"&units=metric&exclude=minutely,daily,alerts&appid={OPENWEATHER_KEY}")
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=1800)
def fetch_open_meteo_forecast(lat, lon):
    try:
        url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
               f"&hourly=temperature_2m,precipitation,weather_code,wind_speed_10m,precipitation_probability,visibility"
               f"&forecast_days=2&timezone=Asia%2FKolkata")
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

@st.cache_data(ttl=1800)
def fetch_tomorrow_io_forecast(lat, lon):
    if not TOMORROWIO_KEY: return None
    try:
        url = (f"https://api.tomorrow.io/v4/weather/forecast?location={lat},{lon}"
               f"&units=metric&apikey={TOMORROWIO_KEY}")
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

def get_daily_summary_and_slabs(hourly_data_list):
    if not hourly_data_list:
        return {"max_temp": "N/A", "min_temp": "N/A", "total_rain": 0, "total_rain_pop": 0, "weather_desc": "N/A", "slabs": []}
    max_temp, min_temp, total_rain_overall = float("-inf"), float("inf"), 0
    all_weather_descs, all_hourly_pops = [], []
    SLAB_DEFINITIONS = [
        (0, 2, "12:30 AM to 02:30 AM"), (2, 4, "02:30 AM to 04:30 AM"),
        (4, 6, "04:30 AM to 06:30 AM"), (6, 8, "06:30 AM to 08:30 AM"),
        (8, 10, "08:30 AM to 10:30 AM"), (10, 12, "10:30 AM to 12:30 PM"),
        (12, 14, "12:30 PM to 02:30 PM"), (14, 16, "02:30 PM to 04:30 PM"),
        (16, 18, "04:30 PM to 06:30 PM"), (18, 20, "06:30 PM to 08:30 PM"),
        (20, 22, "08:30 PM to 10:30 PM"), (22, 2, "10:30 PM to 12:30 AM (Next Day)"),
    ]
    slabs_data_raw = collections.defaultdict(lambda: {
        "rain_mm": 0, "pop": [], "wind_speed": [], "visibility_km": [],
        "lightning": [], "descs": [], "hours_covered": 0
    })
    for dt_ist, data in hourly_data_list:
        max_temp = max(max_temp, data['temp'])
        min_temp = min(min_temp, data['temp'])
        total_rain_overall += data['rain_mm']
        all_weather_descs.append(data['description'])
        all_hourly_pops.append(data['pop'])
        hour_in_day, slab_key = dt_ist.hour, None
        for start_h, end_h, display_name in SLAB_DEFINITIONS:
            if start_h == 22 and end_h == 2:
                if hour_in_day == 22 or hour_in_day == 23:
                    slab_key = (start_h, end_h, display_name)
                    break
            elif start_h < end_h and start_h <= hour_in_day < end_h:
                slab_key = (start_h, end_h, display_name)
                break
        if slab_key:
            raw = slabs_data_raw[slab_key]
            raw["rain_mm"] += data['rain_mm']
            raw["pop"].append(data['pop'])
            raw["wind_speed"].append(data['wind_speed'])
            raw["visibility_km"].append(data.get('visibility_km', 10))
            raw["descs"].append(data['description'])
            raw["lightning"].append(data['lightning'])
            raw["hours_covered"] += 1
    candidate_slabs = []
    for slab_key, slab_data in slabs_data_raw.items():
        if slab_data["hours_covered"] > 0:
            avg_pop = sum(slab_data["pop"]) / len(slab_data["pop"]) if slab_data["pop"] else 0
            avg_wind = sum(slab_data["wind_speed"]) / len(slab_data["wind_speed"]) if slab_data["wind_speed"] else 0
            avg_vis = sum(slab_data["visibility_km"]) / len(slab_data["visibility_km"]) if slab_data["visibility_km"] else 10.0
            main_desc = collections.Counter(slab_data["descs"]).most_common(1)[0][0] if slab_data["descs"] else get_rain_type(slab_data["rain_mm"], is_2hr_slab=True)
            explicit_lightning_in_desc = any("thunder" in d.lower() or "lightning" in d.lower() for d in slab_data["descs"])
            if slab_data["rain_mm"] >= MIN_RAINFALL_FOR_SLAB_DISPLAY_MM:
                candidate_slabs.append({
                    "time_range": slab_key[2],
                    "sort_key": slab_data["rain_mm"] + (avg_pop / 100),
                    "prob": int(round(avg_pop, 0)),
                    "mm": round(slab_data["rain_mm"], 1),
                    "type": get_rain_type(slab_data["rain_mm"], is_2hr_slab=True),
                    "wind_speed": round(avg_wind, 1),
                    "visibility_km": round(avg_vis, 1),
                    "lightning": any(slab_data["lightning"]) or explicit_lightning_in_desc,
                    "description": main_desc
                })
    candidate_slabs.sort(key=lambda x: (-x["sort_key"], x["time_range"]))
    final_slabs, seen_time_ranges = [], set()
    for slab in candidate_slabs:
        if slab["time_range"] not in seen_time_ranges:
            final_slabs.append(slab)
            seen_time_ranges.add(slab["time_range"])
            if len(final_slabs) >= MAX_SLABS_TO_SHOW: break
    slab_order_map = {s[2]: idx for idx, s in enumerate(SLAB_DEFINITIONS)}
    final_slabs.sort(key=lambda x: slab_order_map.get(x["time_range"], float('inf')))
    overall_raw_desc = collections.Counter(all_weather_descs).most_common(1)[0][0] if all_weather_descs else "N/A"
    overall_weather_desc_with_icon = get_rain_type(total_rain_overall, is_2hr_slab=False, overall_description=overall_raw_desc)
    max_hourly_pop = max(all_hourly_pops) if all_hourly_pops else 0
    return {
        "max_temp": round(max_temp, 1) if max_temp != float("-inf") else "N/A",
        "min_temp": round(min_temp, 1) if min_temp != float("inf") else "N/A",
        "total_rain": round(total_rain_overall, 1),
        "total_rain_pop": int(round(max_hourly_pop, 0)),
        "weather_desc": overall_weather_desc_with_icon,
        "slabs": final_slabs
    }

def fetch_consolidated_forecast(lat, lon):
    ow_data = fetch_openweather_forecast(lat, lon)
    om_data = fetch_open_meteo_forecast(lat, lon)
    tm_data = fetch_tomorrow_io_forecast(lat, lon)
    if not any([ow_data, om_data, tm_data]): return None
    hourly_consolidated = {}
    if ow_data and "hourly" in ow_data:
        for entry in ow_data["hourly"]:
            dt_utc = datetime.fromtimestamp(entry["dt"], tz=UTC)
            dt_ist = utc_to_ist(dt_utc)
            hour_key = dt_ist.replace(minute=0, second=0, microsecond=0)
            if hour_key < datetime.now(IST).replace(minute=0, second=0, microsecond=0) - timedelta(hours=1) or \
               hour_key > datetime.now(IST).replace(minute=0, second=0, microsecond=0) + timedelta(hours=48): continue
            hourly_consolidated.setdefault(hour_key, {
                'temp': [], 'rain_mm': [], 'pop': [], 'wind_speed': [],
                'visibility_km': [], 'description': [], 'lightning': []
            })
            hourly_consolidated[hour_key]['temp'].append(entry["temp"])
            rain_mm = entry.get("rain", {}).get("1h", 0)
            snow_mm = entry.get("snow", {}).get("1h", 0)
            hourly_consolidated[hour_key]['rain_mm'].append(rain_mm + snow_mm)
            hourly_consolidated[hour_key]['pop'].append(entry.get("pop", 0) * 100)
            hourly_consolidated[hour_key]['wind_speed'].append(entry["wind_speed"] * 3.6)
            hourly_consolidated[hour_key]['visibility_km'].append(entry.get("visibility", 10000) / 1000)
            if entry.get("weather"):
                hourly_consolidated[hour_key]['description'].append(entry["weather"][0]["description"])
                hourly_consolidated[hour_key]['lightning'].append(200 <= entry["weather"][0]["id"] < 300)
            else:
                hourly_consolidated[hour_key]['description'].append("N/A")
                hourly_consolidated[hour_key]['lightning'].append(False)
    if om_data and "hourly" in om_data:
        times = om_data["hourly"]["time"]
        temps = om_data["hourly"]["temperature_2m"]
        precipitations = om_data["hourly"]["precipitation"]
        weather_codes = om_data["hourly"]["weather_code"]
        wind_speeds = om_data["hourly"]["wind_speed_10m"]
        pops = om_data["hourly"]["precipitation_probability"]
        visibilities = om_data["hourly"].get("visibility", [])
        for i, time_str in enumerate(times):
            dt_ist = datetime.fromisoformat(time_str).replace(tzinfo=IST)
            hour_key = dt_ist.replace(minute=0, second=0, microsecond=0)
            if hour_key < datetime.now(IST).replace(minute=0, second=0, microsecond=0) - timedelta(hours=1) or \
               hour_key > datetime.now(IST).replace(minute=0, second=0, microsecond=0) + timedelta(hours=48): continue
            hourly_consolidated.setdefault(hour_key, {
                'temp': [], 'rain_mm': [], 'pop': [], 'wind_speed': [],
                'visibility_km': [], 'description': [], 'lightning': []
            })
            hourly_consolidated[hour_key]['temp'].append(temps[i])
            hourly_consolidated[hour_key]['rain_mm'].append(precipitations[i])
            hourly_consolidated[hour_key]['pop'].append(pops[i])
            hourly_consolidated[hour_key]['wind_speed'].append(wind_speeds[i])
            hourly_consolidated[hour_key]['visibility_km'].append(visibilities[i]/1000 if visibilities else 10)
            hourly_consolidated[hour_key]['description'].append("OpenMeteo")
            hourly_consolidated[hour_key]['lightning'].append(weather_codes[i] in [95, 96, 99])
    if tm_data and "timelines" in tm_data and "hourly" in tm_data["timelines"]:
        for interval in tm_data["timelines"]["hourly"]:
            dt_iso_str = interval["time"]
            dt_utc_naive = datetime.strptime(dt_iso_str, '%Y-%m-%dT%H:%M:%SZ')
            dt_utc_aware = UTC.localize(dt_utc_naive)
            dt_ist = dt_utc_aware.astimezone(IST)
            hour_key = dt_ist.replace(minute=0, second=0, microsecond=0)
            if hour_key < datetime.now(IST).replace(minute=0, second=0, microsecond=0) - timedelta(hours=1) or \
               hour_key > datetime.now(IST).replace(minute=0, second=0, microsecond=0) + timedelta(hours=48): continue
            values = interval["values"]
            hourly_consolidated.setdefault(hour_key, {
                'temp': [], 'rain_mm': [], 'pop': [], 'wind_speed': [],
                'visibility_km': [], 'description': [], 'lightning': []
            })
            hourly_consolidated[hour_key]['temp'].append(values.get("temperature", 0))
            hourly_consolidated[hour_key]['rain_mm'].append(values.get("precipitationIntensity", 0))
            hourly_consolidated[hour_key]['pop'].append(values.get("precipitationProbability", 0))
            hourly_consolidated[hour_key]['wind_speed'].append(values.get("windSpeed", 0) * 3.6)
            hourly_consolidated[hour_key]['visibility_km'].append(values.get("visibility", 10000) / 1000)
            hourly_consolidated[hour_key]['description'].append("Tomorrow.io")
            lightning_count = values.get("lightningStrikeCount", 0)
            hourly_consolidated[hour_key]['lightning'].append(lightning_count > 0 or values.get("weatherCode") == 8000)
    final_hourly_data = []
    for hour_key in sorted(hourly_consolidated.keys()):
        agg = hourly_consolidated[hour_key]
        avg_temp = sum(agg['temp']) / len(agg['temp']) if agg['temp'] else 0
        avg_rain = sum(agg['rain_mm']) / len(agg['rain_mm']) if agg['rain_mm'] else 0
        avg_pop = sum(agg['pop']) / len(agg['pop']) if agg['pop'] else 0
        avg_wind = sum(agg['wind_speed']) / len(agg['wind_speed']) if agg['wind_speed'] else 0
        avg_vis = sum(agg['visibility_km']) / len(agg['visibility_km']) if agg['visibility_km'] else 10.0
        description = " / ".join(set(agg['description']))
        has_lightning = any(agg['lightning'])
        final_hourly_data.append((hour_key, {
            'temp': avg_temp,
            'rain_mm': avg_rain,
            'pop': avg_pop,
            'wind_speed': avg_wind,
            'visibility_km': avg_vis,
            'description': description,
            'lightning': has_lightning
        }))
    forecast_by_day = collections.defaultdict(list)
    for dt_ist, data in final_hourly_data:
        forecast_by_day[dt_ist.date()].append((dt_ist, data))
    return forecast_by_day

# ---- DASHBOARD UI ----
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
