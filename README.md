# Wartelisten-Kontaktverwaltung

Lokale Desktop-App zur Verwaltung einer Warteliste mit Kontaktdaten. Läuft als Flask-Webserver mit SQLite-Datenbank, bedient über den Browser. Wird als einzelne `.exe` ausgeliefert (Windows) — kein Setup, kein Internet nötig.

## Features

- Kontakte erfassen, bearbeiten, löschen
- Automatisches Ausblenden nach 4 Wochen
- Export/Import als JSON (Backup)
- System-Tray-Integration
- Deutschsprachige Oberfläche

## Installation

1. `Warteliste.exe` von der [Releases-Seite](https://github.com/GrafBunsen/waitlist/releases) herunterladen
2. Einen Ordner im Benutzerverzeichnis anlegen, z. B. `C:\Users\<Name>\Warteliste`
3. Die `.exe` in diesen Ordner verschieben
4. Rechtsklick auf die `.exe` → **Verknüpfung erstellen** → Verknüpfung auf den Desktop ziehen

## Nutzung

- **Starten**: Doppelklick auf die `.exe` oder die Desktop-Verknüpfung. Beim ersten Start erscheint eine Windows-Sicherheitsmeldung ("Windows hat Ihren PC geschützt") — auf **Weitere Informationen** und dann **Trotzdem ausführen** klicken.
- **Bedienung**: Die App öffnet automatisch den Browser. Kontakte können über das Formular links hinzugefügt und in der Tabelle rechts verwaltet werden.
- **System-Tray**: Solange die App läuft, erscheint ein Symbol im System-Tray (neben der Uhr). Darüber kann der Browser erneut geöffnet oder die App beendet werden.
- **Datenbank**: Die Datei `contacts.db` wird im selben Ordner wie die `.exe` gespeichert. Für ein Backup einfach diese Datei kopieren.
- **Mehrfachstart**: Wird die `.exe` erneut gestartet während die App bereits läuft, öffnet sich nur ein neuer Browser-Tab.

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
