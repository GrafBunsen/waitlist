"""Eingabevalidierung und Sanitisierung für die Wartelisten-Kontaktverwaltung.

Schützt gegen XSS durch HTML-Tag-Entfernung (zusätzlich zu Jinja2-Auto-Escaping).
Validiert Pflichtfelder und Import-Datenstrukturen.
"""

import re

# Regex zum Entfernen von HTML-Tags
_HTML_TAG_RE = re.compile(r"<[^>]*>")


def _strip_html(value: str) -> str:
    """Entfernt HTML-Tags aus einem String."""
    return _HTML_TAG_RE.sub("", value)


def _clean_field(value: str) -> str:
    """Bereinigt ein Textfeld: HTML-Tags entfernen und Whitespace trimmen."""
    return _strip_html(value).strip()


def validate_contact(data: dict) -> tuple[bool, dict | list[str]]:
    """Validiert und bereinigt Kontaktdaten.

    Args:
        data: Dict mit Schlüsseln 'name', 'phone', 'email', 'notes'.

    Returns:
        (True, cleaned_data) bei gültigen Daten,
        (False, error_messages) bei ungültigen Daten.
    """
    errors = []

    name = _clean_field(str(data.get("name", "")))
    if not name:
        errors.append("Name ist ein Pflichtfeld und darf nicht leer sein.")

    if errors:
        return False, errors

    cleaned = {
        "name": name,
        "phone": _clean_field(str(data.get("phone", ""))),
        "email": _clean_field(str(data.get("email", ""))),
        "notes": _clean_field(str(data.get("notes", ""))),
    }
    return True, cleaned


def validate_import_json(data: dict) -> tuple[bool, dict | list[str]]:
    """Validiert die Struktur einer Import-JSON-Datei.

    Args:
        data: Dict, das die importierte JSON-Struktur repräsentiert.

    Returns:
        (True, data) bei gültiger Struktur,
        (False, error_messages) bei ungültiger Struktur.
    """
    errors = []

    if not isinstance(data, dict):
        return False, ["Ungültiges JSON-Format: Objekt erwartet."]

    if "version" not in data:
        errors.append("Pflichtfeld 'version' fehlt.")

    if "contacts" not in data:
        errors.append("Pflichtfeld 'contacts' fehlt.")
    elif not isinstance(data["contacts"], list):
        errors.append("'contacts' muss ein Array sein.")
    else:
        for i, contact in enumerate(data["contacts"]):
            if not isinstance(contact, dict):
                errors.append(f"Kontakt {i + 1}: Muss ein Objekt sein.")
                continue
            name = str(contact.get("name", "")).strip()
            if not name:
                errors.append(f"Kontakt {i + 1}: Name ist ein Pflichtfeld und darf nicht leer sein.")

    if errors:
        return False, errors

    return True, data
