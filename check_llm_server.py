#!/usr/bin/env python3
"""
Health check for local LLM server (llama.cpp).
- Between 8-10 AM: start server if down
- Outside 8-10 AM: report status only (don't start - preserve VRAM for Salad)
"""

import datetime
import subprocess
import sys
import os

# Timezone offset: +03:00
TZ_OFFSET = 3
PORT = 8081

def get_local_time():
    """Get current time in +03:00 timezone."""
    utc_now = datetime.datetime.utcnow()
    local_now = utc_now + datetime.timedelta(hours=TZ_OFFSET)
    return local_now

def is_server_running():
    """Check if llama-server is running on port 8081."""
    try:
        result = subprocess.run(
            f"netstat -ano | findstr :{PORT}",
            shell=True,
            capture_output=True,
            text=True
        )
        return result.returncode == 0 and result.stdout.strip() != ""
    except Exception as e:
        return False

def start_server():
    """Start llama-server if not running."""
    server_exe = r"C:\Users\pauti\Downloads\llama-b9553-bin-win-cuda-13.3-x64\cudart-llama-bin-win-cuda-13.3-x64\llama-server.exe"
    model_path = r"C:\Users\pauti\.lmstudio\models\bartowski\Qwen2.5-72B-Instruct-IQ3_XXS\Qwen2.5-72B-Instruct-IQ3_XXS.gguf"
    
    cmd = [
        server_exe,
        "--model", model_path,
        "--port", str(PORT),
        "--n-gpu-layers", "55",
        "--ctx-size", "24576",
        "--batch-size", "512",
        "--flash-attn", "on",
        "--host", "127.0.0.1",
        "-fit", "off"
    ]
    
    # Start in background
    subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    return True

def main():
    now = get_local_time()
    hour = now.hour
    
    print(f"=== LLM Server Health Check ===")
    print(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S')} (+03:00)")
    
    in_window = 8 <= hour < 10
    print(f"Within 8-10 AM window: {in_window}")
    
    server_up = is_server_running()
    print(f"Server status: {'RUNNING' if server_up else 'DOWN'}")
    
    if in_window:
        if not server_up:
            print("Starting server (within 8-10 AM window)...")
            start_server()
            print("Server start command issued.")
        else:
            print("Server already running.")
    else:
        if server_up:
            print("WARNING: Server running outside 8-10 AM window.")
            print("VRAM may not be fully available for Salad.")
        else:
            print("Server down (correct - outside 8-10 AM window).")
            print("VRAM preserved for Salad.")
    
    print(f"=== Check Complete ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
