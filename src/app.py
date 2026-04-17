"""Flask-Anwendung für die Wartelisten-Kontaktverwaltung.

Konfiguriert die Flask-App, definiert alle HTTP-Routes und nutzt
Jinja2-Auto-Escaping für XSS-Schutz.
"""

import json
from datetime import datetime

from flask import (
    Flask,
    abort,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)

from src import db
from src import validators

import os
import sys

if getattr(sys, "frozen", False):
    _base_dir = sys._MEIPASS
else:
    _base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(_base_dir, "templates"),
    static_folder=os.path.join(_base_dir, "static"),
)
app.secret_key = "waitlist-secret-key-local-only"

VISIBILITY_DAYS = 28


@app.template_filter("format_date")
def format_date(value: str) -> str:
    """Formatiert ein Datum von 'YYYY-MM-DD HH:MM:SS' zu 'DD.MM.YY'."""
    try:
        dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d.%m.%y")
    except (ValueError, TypeError):
        return value


def _waiting_days(created_at: str) -> int:
    """Berechnet die Wartedauer in Tagen seit dem Erstellungsdatum."""
    created = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
    return (datetime.now() - created).days


@app.route("/")
def index():
    """Kontaktliste anzeigen (sichtbare oder alle Kontakte)."""
    show_hidden = request.args.get("show_hidden") == "1"

    if show_hidden:
        contacts = db.get_all_contacts()
    else:
        contacts = db.get_visible_contacts(VISIBILITY_DAYS)

    # Wartedauer berechnen und Sichtbarkeitsstatus markieren
    all_contacts = db.get_all_contacts()
    visible_ids = {c["id"] for c in db.get_visible_contacts(VISIBILITY_DAYS)}

    for contact in contacts:
        contact["waiting_days"] = _waiting_days(contact["created_at"])
        contact["is_hidden"] = contact["id"] not in visible_ids

    return render_template(
        "index.html",
        contacts=contacts,
        show_hidden=show_hidden,
        empty_hint=len(contacts) == 0,
        edit_contact=None,
    )


@app.route("/add", methods=["POST"])
def add_contact():
    """Neuen Kontakt validieren und speichern."""
    data = {
        "name": request.form.get("name", ""),
        "phone": request.form.get("phone", ""),
        "email": request.form.get("email", ""),
        "notes": request.form.get("notes", ""),
    }

    is_valid, result = validators.validate_contact(data)

    if not is_valid:
        for error in result:
            flash(error, "error")
        return redirect(url_for("index"))

    db.add_contact(
        name=result["name"],
        phone=result["phone"],
        email=result["email"],
        notes=result["notes"],
    )
    flash("Kontakt erfolgreich hinzugefügt.", "success")
    return redirect(url_for("index"))


@app.route("/edit/<int:contact_id>", methods=["GET"])
def edit_contact(contact_id):
    """Kontaktdaten zum Bearbeiten laden."""
    contact = db.get_contact(contact_id)
    if contact is None:
        abort(404)
    contacts = _get_contacts_for_index()
    return render_template(
        "index.html",
        edit_contact=contact,
        contacts=contacts,
        show_hidden=False,
        empty_hint=len(contacts) == 0,
    )


@app.route("/edit/<int:contact_id>", methods=["POST"])
def update_contact(contact_id):
    """Bearbeiteten Kontakt validieren und aktualisieren."""
    contact = db.get_contact(contact_id)
    if contact is None:
        abort(404)

    data = {
        "name": request.form.get("name", ""),
        "phone": request.form.get("phone", ""),
        "email": request.form.get("email", ""),
        "notes": request.form.get("notes", ""),
    }

    is_valid, result = validators.validate_contact(data)

    if not is_valid:
        for error in result:
            flash(error, "error")
        return redirect(url_for("edit_contact", contact_id=contact_id))

    db.update_contact(
        contact_id,
        name=result["name"],
        phone=result["phone"],
        email=result["email"],
        notes=result["notes"],
    )
    flash("Kontakt erfolgreich aktualisiert.", "success")
    return redirect(url_for("index"))


@app.route("/delete/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):
    """Kontakt löschen."""
    contact = db.get_contact(contact_id)
    if contact is None:
        abort(404)

    db.delete_contact(contact_id)
    flash("Kontakt erfolgreich gelöscht.", "success")
    return redirect(url_for("index"))


@app.route("/export")
def export_contacts():
    """Alle Kontakte als JSON-Datei zum Download anbieten."""
    data = db.export_contacts()
    json_str = json.dumps(data, ensure_ascii=False, indent=2)

    response = make_response(json_str)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.headers["Content-Disposition"] = "attachment; filename=warteliste_export.json"
    return response


@app.route("/import", methods=["GET"])
def import_page():
    """Import-Seite anzeigen."""
    return render_template("import.html")


@app.route("/import", methods=["POST"])
def import_contacts():
    """JSON-Datei importieren mit Modus (ersetzen/zusammenführen)."""
    file = request.files.get("file")
    mode = request.form.get("mode", "replace")

    if not file or file.filename == "":
        flash("Bitte eine JSON-Datei auswählen.", "error")
        return redirect(url_for("import_page"))

    try:
        content = file.read().decode("utf-8")
        data = json.loads(content)
    except (json.JSONDecodeError, UnicodeDecodeError):
        flash("Die Datei enthält kein gültiges JSON-Format.", "error")
        return redirect(url_for("import_page"))

    is_valid, result = validators.validate_import_json(data)

    if not is_valid:
        for error in result:
            flash(error, "error")
        return redirect(url_for("import_page"))

    count = db.import_contacts(data, mode=mode)
    flash(f"{count} Kontakt(e) erfolgreich importiert.", "success")
    return redirect(url_for("index"))


def _get_contacts_for_index():
    """Hilfsfunktion: Kontaktliste mit Wartedauer für die Indexseite."""
    contacts = db.get_visible_contacts(VISIBILITY_DAYS)
    visible_ids = {c["id"] for c in contacts}
    for contact in contacts:
        contact["waiting_days"] = _waiting_days(contact["created_at"])
        contact["is_hidden"] = contact["id"] not in visible_ids
    return contacts


# Datenbank beim Import initialisieren
db.init_db()
