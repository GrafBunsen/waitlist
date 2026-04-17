"""Beispielbasierte Unit-Tests für die UI der Wartelisten-Kontaktverwaltung.

Verwendet den Flask-Test-Client und eine temporäre SQLite-Datenbank.
Jeder Test referenziert die zugehörige Anforderung aus dem Anforderungsdokument.
"""

import io
import json
from datetime import datetime, timedelta

import pytest

from src import db
from src.app import app


@pytest.fixture(autouse=True)
def _use_temp_db(tmp_path, monkeypatch):
    """Jeder Test bekommt eine eigene temporäre Datenbank."""
    db_file = str(tmp_path / "test_contacts.db")
    monkeypatch.setattr(db, "_db_path", lambda: db_file)
    db.init_db()


@pytest.fixture()
def client():
    """Flask-Test-Client."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# Anf. 1.1 – Eingabemaske enthält alle Felder
def test_form_has_required_fields(client):
    """GET / enthält Eingabefelder für Name, Telefonnummer, E-Mail und Notizen."""
    resp = client.get("/")
    html = resp.data.decode()

    assert resp.status_code == 200
    assert 'name="name"' in html
    assert 'name="phone"' in html
    assert 'name="email"' in html
    assert 'name="notes"' in html


# Anf. 2.4 – Leere Liste zeigt Hinweistext
def test_empty_list_shows_hint(client):
    """Wenn keine Kontakte existieren, zeigt GET / den Hinweis 'Warteliste ist leer'."""
    resp = client.get("/")
    html = resp.data.decode()

    assert resp.status_code == 200
    assert "Warteliste ist leer" in html


# Anf. 3.3 – Toggle zeigt ausgeblendete Kontakte
def test_hidden_contacts_toggle(client):
    """GET /?show_hidden=1 zeigt auch Kontakte, die älter als 28 Tage sind."""
    # Kontakt mit Erstellungsdatum vor 35 Tagen einfügen
    old_date = (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%d %H:%M:%S")
    conn = db.get_db()
    try:
        conn.execute(
            "INSERT INTO contacts (name, phone, email, notes, created_at) VALUES (?, ?, ?, ?, ?)",
            ("Alter Kontakt", "123", "alt@test.de", "", old_date),
        )
        conn.commit()
    finally:
        conn.close()

    # Ohne show_hidden: Kontakt nicht sichtbar
    resp_normal = client.get("/")
    html_normal = resp_normal.data.decode()
    assert "Alter Kontakt" not in html_normal

    # Mit show_hidden=1: Kontakt sichtbar
    resp_hidden = client.get("/?show_hidden=1")
    html_hidden = resp_hidden.data.decode()
    assert "Alter Kontakt" in html_hidden


# Anf. 3.4 – Ausgeblendete Kontakte haben CSS-Klasse
def test_hidden_contacts_visual_distinction(client):
    """Ausgeblendete Kontakte haben die CSS-Klasse 'hidden-contact'."""
    old_date = (datetime.now() - timedelta(days=35)).strftime("%Y-%m-%d %H:%M:%S")
    conn = db.get_db()
    try:
        conn.execute(
            "INSERT INTO contacts (name, phone, email, notes, created_at) VALUES (?, ?, ?, ?, ?)",
            ("Versteckter Kontakt", "456", "hidden@test.de", "", old_date),
        )
        conn.commit()
    finally:
        conn.close()

    resp = client.get("/?show_hidden=1")
    html = resp.data.decode()

    assert "hidden-contact" in html
    assert "Versteckter Kontakt" in html


# Anf. 4.1 – Edit-Route zeigt Kontaktdaten
def test_edit_loads_contact_data(client):
    """GET /edit/<id> zeigt die Kontaktdaten im Formular."""
    contact_id = db.add_contact("Maria Muster", "0171-999", "maria@test.de", "Testnotiz")

    resp = client.get(f"/edit/{contact_id}")
    html = resp.data.decode()

    assert resp.status_code == 200
    assert "Maria Muster" in html
    assert "0171-999" in html
    assert "maria@test.de" in html
    assert "Testnotiz" in html


# Anf. 4.3 – Lösch-Button hat Bestätigungsdialog
def test_delete_confirmation(client):
    """Der Lösch-Button enthält einen onclick-confirm-Dialog."""
    contact_id = db.add_contact("Zu Löschen", "", "", "")

    resp = client.get("/")
    html = resp.data.decode()

    assert "confirm(" in html


# Anf. 6.3 – Ungültiges JSON wird abgelehnt
def test_invalid_json_import_rejected(client):
    """POST /import mit ungültigem JSON zeigt eine Fehlermeldung."""
    data = {
        "file": (io.BytesIO(b"das ist kein json!!!"), "bad.json"),
        "mode": "replace",
    }
    resp = client.post("/import", data=data, content_type="multipart/form-data", follow_redirects=True)
    html = resp.data.decode()

    assert "gültiges JSON" in html or "JSON" in html


# Anf. 6.4 – Import-Seite zeigt Modus-Auswahl
def test_import_mode_selection(client):
    """GET /import zeigt Radio-Buttons für Ersetzen/Zusammenführen."""
    resp = client.get("/import")
    html = resp.data.decode()

    assert resp.status_code == 200
    assert 'type="radio"' in html
    assert 'value="replace"' in html
    assert 'value="merge"' in html


# Anf. 7.7 – UI-Texte sind auf Deutsch
def test_german_ui_labels(client):
    """Die UI enthält deutsche Labels wie Name, Telefonnummer, E-Mail, Notizen."""
    resp = client.get("/")
    html = resp.data.decode()

    assert "Name" in html
    assert "Telefonnummer" in html
    assert "E-Mail" in html
    assert "Notizen" in html
