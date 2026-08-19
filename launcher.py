import os
import sys
import time
import socket
import threading
import webbrowser
import uvicorn
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

# Add the backend folder to sys.path so that 'app.main' can be imported correctly
if getattr(sys, 'frozen', False):
    runtime_dir = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    base_dir = Path(sys.executable).parent
    env_path = base_dir / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
else:
    runtime_dir = Path(__file__).resolve().parent
    base_dir = Path(__file__).resolve().parent

backend_dir = runtime_dir / "backend"
if backend_dir.exists():
    sys.path.insert(0, str(backend_dir))

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def wait_for_server(port: int, timeout: int = 30):
    start_time = time.time()
    url = f"http://127.0.0.1:{port}/health"
    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2) as response:
                if response.getcode() == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

def open_browser(port: int):
    # Wait for the server to be ready
    if wait_for_server(port):
        print("Server is ready. Opening browser...")
        webbrowser.open(f"http://127.0.0.1:{port}")
    else:
        print("Error: Server did not start within the timeout period.")

def main():
    port = 8000
    
    if is_port_in_use(port):
        print(f"Warning: Port {port} is already in use. Trying to connect to existing instance...")
        open_browser(port)
        return

    # Start the browser thread
    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    print("Starting server...")
    # Import app.main dynamically after sys.path is updated
    from app.main import app
    
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    main()
