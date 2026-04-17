"""Datenbankschicht für die Wartelisten-Kontaktverwaltung.

Verwendet sqlite3 direkt (kein ORM). Alle Queries nutzen parametrisierte
Platzhalter (?), um SQL-Injection zu verhindern.
"""

import os
import sqlite3
from datetime import datetime

DB_NAME = "contacts.db"


def _db_path() -> str:
    """Gibt den Pfad zur Datenbankdatei im Anwendungsverzeichnis zurück."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, DB_NAME)


def get_db() -> sqlite3.Connection:
    """Gibt eine neue Datenbankverbindung zurück (Row-Factory aktiviert)."""
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Erstellt die Datenbank und das Schema, falls nicht vorhanden."""
    conn = get_db()
    try:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )"""
        )
        conn.commit()
    finally:
        conn.close()


def add_contact(name: str, phone: str = "", email: str = "", notes: str = "") -> int:
    """Fügt einen neuen Kontakt hinzu und gibt die neue ID zurück."""
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO contacts (name, phone, email, notes) VALUES (?, ?, ?, ?)",
            (name, phone, email, notes),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all_contacts() -> list[dict]:
    """Gibt alle Kontakte zurück, sortiert nach Erstellungsdatum (älteste zuerst)."""
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT id, name, phone, email, notes, created_at FROM contacts ORDER BY created_at ASC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_contact(contact_id: int) -> dict | None:
    """Gibt einen einzelnen Kontakt zurück oder None, falls nicht gefunden."""
    conn = get_db()
    try:
        row = conn.execute(
            "SELECT id, name, phone, email, notes, created_at FROM contacts WHERE id = ?",
            (contact_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_contact(contact_id: int, name: str, phone: str = "", email: str = "", notes: str = "") -> bool:
    """Aktualisiert einen Kontakt. Gibt True zurück, wenn der Kontakt existierte."""
    conn = get_db()
    try:
        cursor = conn.execute(
            "UPDATE contacts SET name = ?, phone = ?, email = ?, notes = ? WHERE id = ?",
            (name, phone, email, notes, contact_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_contact(contact_id: int) -> bool:
    """Löscht einen Kontakt. Gibt True zurück, wenn der Kontakt existierte."""
    conn = get_db()
    try:
        cursor = conn.execute(
            "DELETE FROM contacts WHERE id = ?",
            (contact_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def get_visible_contacts(visibility_days: int = 28) -> list[dict]:
    """Gibt Kontakte zurück, deren Erstellungsdatum innerhalb der Sichtbarkeitsfrist liegt."""
    conn = get_db()
    try:
        cutoff = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows = conn.execute(
            """SELECT id, name, phone, email, notes, created_at FROM contacts
               WHERE julianday(?) - julianday(created_at) <= ?
               ORDER BY created_at ASC""",
            (cutoff, visibility_days),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def export_contacts() -> dict:
    """Exportiert alle Kontakte als Dict mit Version, Zeitstempel und Kontaktliste (ohne ID)."""
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT name, phone, email, notes, created_at FROM contacts ORDER BY created_at ASC"
        ).fetchall()
        return {
            "version": 1,
            "exported_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "contacts": [dict(row) for row in rows],
        }
    finally:
        conn.close()


def import_contacts(data: dict, mode: str = "replace") -> int:
    """Importiert Kontakte aus einem Export-Dict.

    Args:
        data: Dict mit 'contacts'-Array (jeder Eintrag hat name, phone, email, notes, created_at).
        mode: 'replace' löscht alle bestehenden Kontakte vor dem Import,
              'merge' fügt die Kontakte zu den bestehenden hinzu.

    Returns:
        Anzahl der importierten Kontakte.
    """
    contacts = data.get("contacts", [])
    conn = get_db()
    try:
        if mode == "replace":
            conn.execute("DELETE FROM contacts")

        count = 0
        for contact in contacts:
            conn.execute(
                "INSERT INTO contacts (name, phone, email, notes, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    contact.get("name", ""),
                    contact.get("phone", ""),
                    contact.get("email", ""),
                    contact.get("notes", ""),
                    contact.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                ),
            )
            count += 1

        conn.commit()
        return count
    finally:
        conn.close()
