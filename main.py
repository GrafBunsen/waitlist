"""Einstiegspunkt für die Wartelisten-Kontaktverwaltung.

Startet den Flask-Server in einem Daemon-Thread, öffnet den Standard-Browser
und zeigt ein System-Tray-Icon im Hauptthread an.
"""

import os
import sys
import threading
import webbrowser

from src.app import app
from src.tray import run_tray

HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}"


def start_server() -> None:
    """Startet den Flask-Server (blockierend, für Daemon-Thread gedacht)."""
    app.run(host=HOST, port=PORT, use_reloader=False)


def open_browser() -> None:
    """Öffnet die App-URL im Standard-Browser."""
    webbrowser.open(URL)


def quit_app() -> None:
    """Beendet die Anwendung sauber."""
    os._exit(0)


def main() -> None:
    """Hauptfunktion: Server starten, Browser öffnen, Tray-Icon anzeigen."""
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    open_browser()

    run_tray(
        open_browser_callback=open_browser,
        quit_callback=quit_app,
    )


if __name__ == "__main__":
    main()
