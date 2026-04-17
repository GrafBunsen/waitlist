"""Property-basierte Tests für die Wartelisten-Kontaktverwaltung.

Verwendet Hypothesis für generierte Eingaben und pytest für die Testinfrastruktur.
Jeder Test referenziert die zugehörige Korrektheitseigenschaft aus dem Design-Dokument.
"""

import os
import tempfile
from datetime import datetime, timedelta

import pytest
from hypothesis import given, settings, strategies as st

from src.app import _waiting_days
from src import db
from src import validators


@pytest.fixture(autouse=True)
def _use_temp_db(tmp_path, monkeypatch):
    """Jeder Test bekommt eine eigene temporäre Datenbank."""
    db_file = str(tmp_path / "test_contacts.db")
    monkeypatch.setattr(db, "_db_path", lambda: db_file)
    db.init_db()


# Strategien für gültige Kontaktdaten
valid_name = st.text(min_size=1).filter(lambda s: s.strip())
optional_field = st.text()


# Feature: waitlist-contact-manager, Property 1: Kontakt-Persistenz Round-Trip
@settings(max_examples=100)
@given(
    name=valid_name,
    phone=optional_field,
    email=optional_field,
    notes=optional_field,
)
def test_contact_persistence_roundtrip(name, phone, email, notes):
    """Für beliebige gültige Kontaktdaten ergibt Speichern und Lesen
    identische Felder mit gültigem Erstellungsdatum.

    Validiert: Anforderungen 1.2, 1.5, 5.3
    """
    contact_id = db.add_contact(name, phone, email, notes)
    loaded = db.get_contact(contact_id)

    assert loaded is not None
    assert loaded["name"] == name
    assert loaded["phone"] == phone
    assert loaded["email"] == email
    assert loaded["notes"] == notes
    assert loaded["id"] == contact_id

    # Erstellungsdatum muss ein gültiges Datum sein
    created = datetime.strptime(loaded["created_at"], "%Y-%m-%d %H:%M:%S")
    assert isinstance(created, datetime)


# Feature: waitlist-contact-manager, Property 7: Löschung entfernt Kontakt vollständig
@settings(max_examples=100, deadline=None)
@given(
    name=valid_name,
    phone=optional_field,
    email=optional_field,
    notes=optional_field,
)
def test_delete_removes_contact(name, phone, email, notes):
    """Nach Löschung ist der Kontakt nicht mehr in der DB und die Anzahl sinkt um eins.

    Validiert: Anforderung 4.4
    """
    contact_id = db.add_contact(name, phone, email, notes)
    count_before = len(db.get_all_contacts())

    deleted = db.delete_contact(contact_id)

    assert deleted is True
    assert db.get_contact(contact_id) is None
    assert len(db.get_all_contacts()) == count_before - 1


# Feature: waitlist-contact-manager, Property 2: Whitespace-Namen werden abgelehnt
@settings(max_examples=100)
@given(
    name=st.from_regex(r"[\s]*", fullmatch=True),
)
def test_whitespace_names_rejected(name):
    """Strings aus nur Whitespace-Zeichen (einschließlich leerer String)
    werden von der Validierung abgelehnt.

    Validiert: Anforderung 1.4
    """
    data = {"name": name, "phone": "", "email": "", "notes": ""}
    is_valid, result = validators.validate_contact(data)

    assert is_valid is False
    assert isinstance(result, list)
    assert len(result) > 0


# Feature: waitlist-contact-manager, Property 3: Korrekte Wartedauer-Berechnung
@settings(max_examples=100)
@given(
    days_ago=st.integers(min_value=0, max_value=3650),
)
def test_waiting_duration_calculation(days_ago):
    """Für beliebige Erstellungsdaten entspricht die Wartedauer exakt der
    Tagesdifferenz zwischen Erstellungsdatum und aktuellem Datum.

    **Validates: Requirements 2.2**
    """
    now = datetime.now()
    created_date = now - timedelta(days=days_ago)
    created_at_str = created_date.strftime("%Y-%m-%d %H:%M:%S")

    result = _waiting_days(created_at_str)
    expected = (datetime.now() - created_date).days

    assert result == expected


# Feature: waitlist-contact-manager, Property 4: Sortierung nach Erstellungsdatum
@settings(max_examples=100)
@given(
    data=st.lists(
        st.tuples(
            valid_name,
            optional_field,
            optional_field,
            optional_field,
            st.datetimes(
                min_value=datetime(2020, 1, 1),
                max_value=datetime(2030, 12, 31),
            ),
        ),
        min_size=1,
        max_size=20,
    ),
)
def test_contacts_sorted_by_date(data):
    """Die Kontaktliste ist immer aufsteigend nach Erstellungsdatum sortiert,
    unabhängig von der Einfügereihenfolge.

    Validiert: Anforderung 2.3
    """
    contacts_for_import = []
    for name, phone, email, notes, created_dt in data:
        contacts_for_import.append(
            {
                "name": name,
                "phone": phone,
                "email": email,
                "notes": notes,
                "created_at": created_dt.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    db.import_contacts({"contacts": contacts_for_import}, mode="replace")

    result = db.get_all_contacts()

    assert len(result) == len(data)

    dates = [r["created_at"] for r in result]
    assert dates == sorted(dates), "Kontaktliste ist nicht aufsteigend nach created_at sortiert"


# Feature: waitlist-contact-manager, Property 5: Sichtbarkeitsfilterung bewahrt Datenintegrität
@settings(max_examples=100, deadline=None)
@given(
    data=st.lists(
        st.tuples(
            valid_name,
            optional_field,
            optional_field,
            optional_field,
            st.integers(min_value=0, max_value=120),
        ),
        min_size=1,
        max_size=15,
    ),
    visibility_days=st.integers(min_value=1, max_value=90),
)
def test_visibility_filtering(data, visibility_days):
    """Filterung gibt genau die Kontakte innerhalb der Frist zurück,
    alle bleiben in der DB.

    **Validates: Requirements 3.1, 3.2**
    """
    now = datetime.now()

    contacts_for_import = []
    for name, phone, email, notes, days_ago in data:
        created_dt = now - timedelta(days=days_ago)
        contacts_for_import.append(
            {
                "name": name,
                "phone": phone,
                "email": email,
                "notes": notes,
                "created_at": created_dt.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    db.import_contacts({"contacts": contacts_for_import}, mode="replace")

    total_count = len(db.get_all_contacts())
    visible = db.get_visible_contacts(visibility_days)

    # Sichtbare Kontakte sind genau die innerhalb der Frist.
    # Wir verwenden days_ago < visibility_days (strikt kleiner) für eindeutig sichtbare
    # Kontakte, da bei days_ago == visibility_days eine Timing-Differenz zwischen
    # dem now() im Test und dem now() in get_visible_contacts dazu führen kann,
    # dass der Kontakt knapp über die Grenze rutscht.
    clearly_visible = sum(
        1 for _, _, _, _, days_ago in data if days_ago < visibility_days
    )
    clearly_hidden = sum(
        1 for _, _, _, _, days_ago in data if days_ago > visibility_days
    )
    assert len(visible) >= clearly_visible, (
        f"Erwartet mindestens {clearly_visible} sichtbare Kontakte, "
        f"aber nur {len(visible)} erhalten (visibility_days={visibility_days})"
    )
    assert len(visible) <= len(data) - clearly_hidden, (
        f"Erwartet höchstens {len(data) - clearly_hidden} sichtbare Kontakte, "
        f"aber {len(visible)} erhalten (visibility_days={visibility_days})"
    )

    # Alle Kontakte bleiben in der DB (keine Löschung durch Filterung)
    assert total_count == len(data), (
        f"Erwartet {len(data)} Kontakte in der DB, aber {total_count} gefunden"
    )


# Feature: waitlist-contact-manager, Property 6: Update-Persistenz
@settings(max_examples=100)
@given(
    name=valid_name,
    phone=optional_field,
    email=optional_field,
    notes=optional_field,
    new_name=valid_name,
    new_phone=optional_field,
    new_email=optional_field,
    new_notes=optional_field,
)
def test_update_persistence(
    name, phone, email, notes, new_name, new_phone, new_email, new_notes
):
    """Nach Update enthält die DB die neuen Werte, Erstellungsdatum bleibt unverändert.

    **Validates: Requirements 4.2**
    """
    # Kontakt anlegen und created_at merken
    contact_id = db.add_contact(name, phone, email, notes)
    original = db.get_contact(contact_id)
    assert original is not None
    original_created_at = original["created_at"]

    # Kontakt mit neuen Werten aktualisieren
    updated = db.update_contact(contact_id, new_name, new_phone, new_email, new_notes)
    assert updated is True

    # Aktualisierte Daten aus der DB lesen
    loaded = db.get_contact(contact_id)
    assert loaded is not None

    # Neue Werte müssen in der DB stehen
    assert loaded["name"] == new_name
    assert loaded["phone"] == new_phone
    assert loaded["email"] == new_email
    assert loaded["notes"] == new_notes

    # Erstellungsdatum darf sich nicht geändert haben
    assert loaded["created_at"] == original_created_at


# Feature: waitlist-contact-manager, Property 8: Export/Import Round-Trip
@settings(max_examples=100)
@given(
    data=st.lists(
        st.tuples(
            valid_name,
            optional_field,
            optional_field,
            optional_field,
            st.datetimes(
                min_value=datetime(2020, 1, 1),
                max_value=datetime(2030, 12, 31),
            ),
        ),
        min_size=0,
        max_size=20,
    ),
)
def test_export_import_roundtrip(data):
    """Exportieren und Importieren (Ersetzen-Modus) ergibt identische Kontaktliste.

    **Validates: Requirements 6.5**
    """
    # Kontakte mit explizitem created_at über import_contacts einfügen
    contacts_for_import = []
    for name, phone, email, notes, created_dt in data:
        contacts_for_import.append(
            {
                "name": name,
                "phone": phone,
                "email": email,
                "notes": notes,
                "created_at": created_dt.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    db.import_contacts({"contacts": contacts_for_import}, mode="replace")

    # Exportieren
    exported = db.export_contacts()

    # DB leeren und exportierte Daten im Ersetzen-Modus importieren
    db.import_contacts(exported, mode="replace")

    # Ergebnis lesen und mit Original vergleichen
    result = db.get_all_contacts()

    assert len(result) == len(data)

    # Kontakte nach created_at sortiert vergleichen (DB gibt sortiert zurück)
    original_sorted = sorted(contacts_for_import, key=lambda c: c["created_at"])

    for original, reimported in zip(original_sorted, result):
        assert reimported["name"] == original["name"]
        assert reimported["phone"] == original["phone"]
        assert reimported["email"] == original["email"]
        assert reimported["notes"] == original["notes"]
        assert reimported["created_at"] == original["created_at"]
