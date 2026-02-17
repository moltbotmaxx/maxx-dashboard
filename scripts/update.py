import json
import os
import subprocess
import time
from datetime import datetime

# Configuration
WORKSPACE = "/Users/maxx/.openclaw/workspace"
PROJECT_DIR = os.path.join(WORKSPACE, "smart-frame")
DATA_FILE = os.path.join(PROJECT_DIR, "data.json")
HTML_FILE = os.path.join(PROJECT_DIR, "index.html")
FTP_HOST = "192.168.100.12"
FTP_PORT = "2221"

# Weather code to emoji mapping
WEATHER_CODES = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
    45: "🌫️", 48: "🌫️",
    51: "🌦️", 53: "🌦️", 55: "🌧️",
    61: "🌧️", 63: "🌧️", 65: "🌧️",
    71: "❄️", 73: "❄️", 75: "❄️",
    80: "🌦️", 81: "🌧️", 82: "🌧️",
    95: "⛈️", 96: "⛈️", 99: "⛈️",
}

def code_to_icon(code):
    return WEATHER_CODES.get(code, "🌤️")

def code_to_condition(code):
    if code == 0: return "Cielo Despejado"
    elif code <= 3: return "Parcialmente Nublado"
    elif code <= 48: return "Niebla"
    elif code <= 55: return "Llovizna"
    elif code <= 65: return "Lluvia"
    elif code <= 75: return "Nieve"
    elif code <= 82: return "Chubascos"
    elif code >= 95: return "Tormenta"
    return "Variable"

def update_data():
    print("Updating data...")
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    # Fetch weather with full hourly + daily data
    try:
        api_url = (
            'https://api.open-meteo.com/v1/forecast'
            '?latitude=10.0163&longitude=-84.2116'
            '&current_weather=true'
            '&hourly=temperature_2m,weathercode,apparent_temperature,relative_humidity_2m'
            '&daily=temperature_2m_max,temperature_2m_min,uv_index_max,precipitation_probability_max'
            '&timezone=America/Costa_Rica'
            '&forecast_days=1'
        )
        res = subprocess.check_output(['curl', '-s', api_url], text=True)
        api = json.loads(res)
        w = api['current_weather']

        data['weather']['temp_c'] = str(round(w['temperature']))
        data['weather']['wind_kmh'] = str(round(w['windspeed']))
        data['weather']['condition'] = code_to_condition(w.get('weathercode', 0))

        # Daily
        if 'daily' in api:
            d = api['daily']
            data['weather']['max_temp_c'] = str(round(d['temperature_2m_max'][0]))
            data['weather']['min_temp_c'] = str(round(d['temperature_2m_min'][0]))
            data['weather']['uv_index'] = str(round(d['uv_index_max'][0]))
            data['weather']['prob_rain'] = str(round(d['precipitation_probability_max'][0]))

        # Feels like + humidity from hourly
        current_hour = datetime.now().hour
        if 'hourly' in api:
            h = api['hourly']
            if 'apparent_temperature' in h and current_hour < len(h['apparent_temperature']):
                data['weather']['feels_like_c'] = str(round(h['apparent_temperature'][current_hour]))
            if 'relative_humidity_2m' in h and current_hour < len(h['relative_humidity_2m']):
                data['weather']['humidity'] = str(round(h['relative_humidity_2m'][current_hour]))

            # Hourly forecast (next 3 time slots)
            hourly_temps = h.get('temperature_2m', [])
            hourly_codes = h.get('weathercode', [])
            hourly_times = h.get('time', [])
            forecast = []
            for offset in [3, 6, 9]:
                idx = current_hour + offset
                if idx < len(hourly_temps) and idx < len(hourly_codes):
                    t = datetime.fromisoformat(hourly_times[idx])
                    forecast.append({
                        "time": t.strftime("%-I%p"),
                        "icon": code_to_icon(hourly_codes[idx]),
                        "temp": str(round(hourly_temps[idx]))
                    })
            if forecast:
                data['weather']['hourly_forecast'] = forecast

    except Exception as e:
        print(f"Weather update failed: {e}")

    # Update date + last update
    now = datetime.now()
    data['maxx_status']['date'] = now.strftime("%A, %d %b").capitalize()
    data['maxx_status']['last_update_time'] = now.strftime("%H:%M")

    # Save
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    return data

def generate_and_upload():
    # Capture current counter
    try:
        res = subprocess.check_output(['lftp', '-c', f'open ftp://{FTP_HOST}:{FTP_PORT}; ls'], text=True)
        existing = [line.split()[-1] for line in res.strip().split('\n') if 'Dashboard_' in line]
        nums = [int(f.split('_')[1].split('.')[0]) for f in existing if '_' in f]
        last_num = max(nums) if nums else 0
    except:
        last_num = 0

    new_num_1 = last_num + 1
    new_num_2 = last_num + 2

    file_1 = f"Dashboard_{new_num_1:05d}.png"
    file_2 = f"Dashboard_{new_num_2:05d}.png"

    print(f"Generating {file_1} and {file_2}...")

if __name__ == "__main__":
    data = update_data()
    print("Automation script ready. Data updated with hourly forecast.")
