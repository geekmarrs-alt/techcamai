import multiprocessing
import os
import sys
import time
import subprocess
import signal

# For the repo root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
API_DIR = os.path.join(BASE_DIR, "api")

def start_api():
    """Run the FastAPI server as a separate process."""
    env = os.environ.copy()
    env["PYTHONPATH"] = API_DIR
    # Default to local storage for Windows desktop use
    if "DB_PATH" not in env:
        env["DB_PATH"] = os.path.join(BASE_DIR, "techcamai.db")
    if "CLIPS_DIR" not in env:
        env["CLIPS_DIR"] = os.path.join(BASE_DIR, "clips")

    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
    return subprocess.Popen(cmd, env=env, cwd=API_DIR)

def start_worker():
    """Run the detection worker."""
    env = os.environ.copy()
    env["API_BASE_URL"] = "http://127.0.0.1:8000"
    cmd = [sys.executable, "worker/worker.py"]
    return subprocess.Popen(cmd, env=env, cwd=BASE_DIR)

def main():
    print("TECHCAMAI Desktop - Starting services...")
    api_proc = start_api()
    time.sleep(2) # Give API time to boot
    worker_proc = start_worker()

    try:
        import webview
        print("Launching desktop window...")
        # Frameless/Custom frames in pywebview can be tricky on Windows;
        # using standard window with translucent background if possible.
        webview.create_window(
            'TECHCAMAI AI CCTV Console',
            'http://127.0.0.1:8000',
            width=1280,
            height=860,
            min_size=(1024, 720),
            background_color='#050a14'
        )
        webview.start()
    except ImportError:
        print("pywebview not found. Running in 'Headless' Desktop mode.")
        print("Open http://127.0.0.1:8000 in your browser.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    finally:
        print("Shutting down...")
        api_proc.terminate()
        worker_proc.terminate()

if __name__ == "__main__":
    # On Windows, need this for multiprocessing if using pyinstaller
    multiprocessing.freeze_support()
    main()
