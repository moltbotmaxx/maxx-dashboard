import os
import subprocess
import time
from datetime import datetime

# Configuration
WORKSPACE = "/Users/maxx/.openclaw/workspace"
PROJECT_DIR = os.path.join(WORKSPACE, "projects", "smart-frame")
LATEST_PNG = os.path.join(PROJECT_DIR, "Dashboard_Latest.png")
COUNTER_FILE = os.path.join(PROJECT_DIR, "upload_counter.txt")

FTP_HOST = "192.168.100.12"
FTP_PORT = "2221"

def get_next_frame_number():
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            f.write("1")
        return 1
    
    with open(COUNTER_FILE, "r") as f:
        try:
            val = int(f.read().strip())
        except:
            val = 0
    
    next_val = val + 1
    with open(COUNTER_FILE, "w") as f:
        f.write(str(next_val))
    return next_val

def sync_strict():
    print(f"[{datetime.now()}] 🛡️ Initiating STRICT SEQUENTIAL SYNC (Frame_X Protocol)...")
    
    if not os.path.exists(LATEST_PNG):
        print(f"❌ Error: {LATEST_PNG} not found.")
        return

    try:
        # Get sequential number
        frame_num = get_next_frame_number()
        final_filename = f"Frame_{frame_num}.png"
        temp_name = f"sync_buffer_{frame_num}.png"
        
        print(f"Target Sequence: {final_filename}")

        # 1. Clean up old Frame_ files to prevent storage bloat, but KEEP current one
        # Note: If the frame logic requires multiple, we adjust. 
        # Usually, consecutive means Frame_1, Frame_2... and the frame picks the highest.
        
        # 2. Upload with a temporary name to ensure atomicity
        print(f"Uploading temporary buffer: {temp_name}...")
        subprocess.check_call([
            'curl', '-s', '-T', LATEST_PNG, 
            f'ftp://{FTP_HOST}:{FTP_PORT}/{temp_name}'
        ])

        # 3. Atomic Rename to sequential final name
        print(f"Executing atomic switch to {final_filename}...")
        subprocess.check_call(['lftp', '-c', f'''
            open ftp://{FTP_HOST}:{FTP_PORT};
            mv {temp_name} {final_filename}
        '''], shell=True)

        # 4. Optional: Remove very old frames if needed to save space on the target
        # For now, we prioritize keeping the sequence as requested.

        print(f"✅ Strict Sync Success. Sequence {final_filename} deployed.")

    except Exception as e:
        print(f"❌ STRICT SEQUENTIAL SYNC FAILED: {e}")

if __name__ == "__main__":
    sync_strict()
