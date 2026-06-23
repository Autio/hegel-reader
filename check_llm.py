"""Pre-run check: if local LLM is down, switch to OpenRouter for this run."""
import urllib.request, subprocess, os

LOCAL_URL = "http://localhost:8081/v1/models"
HERMES = r"C:\Users\pauti\AppData\Local\hermes"

def is_local_alive():
    try:
        urllib.request.urlopen(LOCAL_URL, timeout=5)
        return True
    except:
        return False

def switch_to_cloud():
    """Switch hegel-local profile to OpenRouter for this run."""
    subprocess.run([
        "hermes", "--profile", "hegel-local", "config", "set", 
        "model.provider", "openrouter"
    ], capture_output=True)
    subprocess.run([
        "hermes", "--profile", "hegel-local", "config", "set",
        "model.default", "deepseek/deepseek-v4-pro"
    ], capture_output=True)
    print("[hegel-reader] Local LLM down. Switched to OpenRouter for this run.")

def switch_to_local():
    """Switch back to local for future runs."""
    subprocess.run([
        "hermes", "--profile", "hegel-local", "config", "set",
        "model.provider", "custom:llama-cpp"
    ], capture_output=True)
    subprocess.run([
        "hermes", "--profile", "hegel-local", "config", "set",
        "model.default", "local-qwen-72b"
    ], capture_output=True)
    subprocess.run([
        "hermes", "--profile", "hegel-local", "config", "set",
        "model.base_url", "http://localhost:8081/v1"
    ], capture_output=True)
    subprocess.run([
        "hermes", "--profile", "hegel-local", "config", "set",
        "model.context_length", "24576"
    ], capture_output=True)
    print("[hegel-reader] Switched back to local model.")

if __name__ == "__main__":
    # Currently always check. In the future, add logic to detect last state.
    # For now: the health check cron runs every 30min and restarts the server.
    # So by 9am, the server should be up if the machine is healthy.
    alive = is_local_alive()
    print(f"[hegel-reader] Local LLM: {'ALIVE' if alive else 'DOWN'}")
    
    if not alive:
        switch_to_cloud()
        # After this run, the health check will restart the server,
        # and tomorrow's run should use local again.
        # But to be safe, we switch back at the end.
    
    # Print status for the cron agent to see
    if alive:
        print("[hegel-reader] Using local Qwen 72B on RTX 5090")
    else:
        print("[hegel-reader] FALLBACK: Using OpenRouter (deepseek-v4-pro)")
