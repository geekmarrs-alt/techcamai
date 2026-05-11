"""
TECHCAMAI Desktop Application

Double-click to launch. No Python install needed when built with PyInstaller.
Starts the operator dashboard and opens it in the default browser.
"""
from __future__ import annotations

import os
import sys
import socket
import threading
import time
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox

HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}/"


def _base_dir() -> str:
    """Directory where the .exe lives (or repo root when running from source)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _resource_dir() -> str:
    """Directory where bundled code/templates live (PyInstaller _MEIPASS or repo root)."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS  # type: ignore[attr-defined]
    return os.path.dirname(os.path.abspath(__file__))


def _setup_environment() -> None:
    base = _base_dir()
    resource = _resource_dir()

    data_dir = os.path.join(base, "data")
    clips_dir = os.path.join(data_dir, "clips")
    db_path = os.path.join(data_dir, "techcamai.db")

    os.makedirs(clips_dir, exist_ok=True)

    os.environ["DB_PATH"] = db_path
    os.environ["CLIPS_DIR"] = clips_dir

    api_dir = os.path.join(resource, "api")
    if api_dir not in sys.path:
        sys.path.insert(0, api_dir)


def _port_in_use() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((HOST, PORT)) == 0


class TechcamaiApp:
    def __init__(self) -> None:
        self.server_thread: threading.Thread | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.root = tk.Tk()
        self.root.title("TECHCAMAI")
        self.root.geometry("420x300")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f172a")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Header.TLabel", background="#0f172a", foreground="#38bdf8",
                        font=("Segoe UI", 22, "bold"))
        style.configure("Sub.TLabel", background="#0f172a", foreground="#94a3b8",
                        font=("Segoe UI", 10))
        style.configure("Status.TLabel", background="#0f172a", foreground="#22c55e",
                        font=("Segoe UI", 11))
        style.configure("Url.TLabel", background="#0f172a", foreground="#60a5fa",
                        font=("Segoe UI", 11, "underline"))
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), padding=8)

        main = tk.Frame(self.root, bg="#0f172a", padx=30, pady=20)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="TECHCAMAI", style="Header.TLabel").pack(pady=(10, 0))
        ttk.Label(main, text="Edge Camera Monitoring", style="Sub.TLabel").pack()

        sep = ttk.Separator(main, orient="horizontal")
        sep.pack(fill="x", pady=12)

        self.status_label = ttk.Label(main, text="Starting...", style="Status.TLabel")
        self.status_label.pack()

        self.url_label = ttk.Label(main, text=URL, style="Url.TLabel", cursor="hand2")
        self.url_label.pack(pady=(4, 0))
        self.url_label.bind("<Button-1>", lambda _: webbrowser.open(URL))

        btn_frame = tk.Frame(main, bg="#0f172a")
        btn_frame.pack(pady=18)

        self.open_btn = ttk.Button(btn_frame, text="Open Dashboard",
                                   style="Action.TButton", command=self._open_dashboard)
        self.open_btn.pack(side="left", padx=8)
        self.open_btn.state(["disabled"])

        self.stop_btn = ttk.Button(btn_frame, text="Stop && Exit",
                                   style="Action.TButton", command=self._on_close)
        self.stop_btn.pack(side="left", padx=8)

        ttk.Label(main, text="LAN scan available at /ui/scan", style="Sub.TLabel").pack(
            side="bottom", pady=(8, 0))

    def start(self) -> None:
        if _port_in_use():
            messagebox.showerror(
                "Port in use",
                f"Port {PORT} is already in use.\n\n"
                "Close the other application using that port and try again.",
            )
            self.root.destroy()
            return

        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()

        self.root.after(500, self._poll_ready)
        self.root.mainloop()

    def _run_server(self) -> None:
        import uvicorn
        from app.main import app  # noqa: E402

        uvicorn.run(app, host=HOST, port=PORT, log_level="warning")

    def _poll_ready(self) -> None:
        if _port_in_use():
            self.status_label.configure(text="Running", foreground="#22c55e")
            self.open_btn.state(["!disabled"])
            webbrowser.open(URL)
        else:
            self.root.after(500, self._poll_ready)

    def _open_dashboard(self) -> None:
        webbrowser.open(URL)

    def _on_close(self) -> None:
        self.root.destroy()
        os._exit(0)


def main() -> None:
    _setup_environment()
    app = TechcamaiApp()
    app.start()


if __name__ == "__main__":
    main()
