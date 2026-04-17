# Wartelisten-Kontaktverwaltung

Lokale Desktop-App zur Verwaltung einer Warteliste mit Kontaktdaten. Läuft als Flask-Webserver mit SQLite-Datenbank, bedient über den Browser. Wird als einzelne `.exe` ausgeliefert (Windows) — kein Setup, kein Internet nötig.

## Features

- Kontakte erfassen, bearbeiten, löschen
- Automatisches Ausblenden nach 4 Wochen
- Export/Import als JSON (Backup)
- System-Tray-Integration
- Deutschsprachige Oberfläche

## Entwicklung

```bash
# Abhängigkeiten installieren
uv sync --all-extras

# Server starten (Entwicklung)
uv run flask --app src.app run --port 5000

# Tests ausführen
uv run pytest tests/ -v
```

## Build (Windows .exe)

Auf einer Windows-Maschine:

```bash
pip install pyinstaller flask pystray pillow
pyinstaller build.spec
```

Die fertige `Warteliste.exe` liegt in `dist/`.

## Projektstruktur

```
├── main.py          # Einstiegspunkt (Server + Tray)
├── src/
│   ├── app.py       # Flask-App + Routes
│   ├── db.py        # SQLite-Datenbankschicht
│   ├── tray.py      # System-Tray (pystray)
│   └── validators.py
├── templates/       # Jinja2-Templates
├── static/          # CSS + JS
├── tests/           # pytest + Hypothesis
├── build.spec       # PyInstaller-Konfiguration
└── pyproject.toml
```
