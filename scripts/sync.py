import json
import os
import subprocess
from datetime import datetime

# Config
WORKSPACE = "/Users/maxx/.openclaw/workspace"
PROJECT_DIR = os.path.join(WORKSPACE, "smart-frame")
DATA_FILE = os.path.join(PROJECT_DIR, "data.json")
HTML_FILE = os.path.join(PROJECT_DIR, "index.html")
FTP_HOST = "192.168.100.12"
FTP_PORT = "2221"

def update():
    now = datetime.now().strftime("%H:%M")
    print(f"[{now}] Starting sync...")

    # 1. Update Data (Weather)
    try:
        res = subprocess.check_output(['curl', '-s', 'https://api.open-meteo.com/v1/forecast?latitude=10.0163&longitude=-84.2116&current_weather=true'], text=True)
        w = json.loads(res)['current_weather']
        
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        
        data['weather']['temp_c'] = str(round(w['temperature']))
        data['weather']['wind_kmh'] = str(round(w['windspeed']))
        data['maxx_status']['date'] = datetime.now().strftime("%A, %d %b").capitalize()
        
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
            
        # Update HTML "last update" text
        with open(HTML_FILE, 'r') as f:
            content = f.read()
        
        import re
        content = re.sub(r'Last update: \d{2}:\d{2}', f'Last update: {now}', content)
        # Also update the hardcoded values for reliable screenshot
        content = re.sub(r'id="w-temp">\d+°', f'id="w-temp">{data["weather"]["temp_c"]}°', content)
        
        with open(HTML_FILE, 'w') as f:
            f.write(content)
            
    except Exception as e:
        print(f"Error updating data: {e}")

    # Note: Screenshot and FTP upload will be handled by the agent turn 
    # since it has access to the 'browser' and 'exec' tools.
    print("Local files updated. Ready for screenshot and upload.")

if __name__ == "__main__":
    update()
