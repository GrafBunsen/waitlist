"""Tests für validators.py – Eingabevalidierung und Sanitisierung."""

import pytest

from src.validators import validate_contact, validate_import_json


# --- validate_contact ---


class TestValidateContact:
    def test_valid_contact_all_fields(self):
        data = {"name": "Max", "phone": "123", "email": "a@b.de", "notes": "Test"}
        ok, cleaned = validate_contact(data)
        assert ok is True
        assert cleaned["name"] == "Max"
        assert cleaned["phone"] == "123"
        assert cleaned["email"] == "a@b.de"
        assert cleaned["notes"] == "Test"

    def test_valid_contact_name_only(self):
        data = {"name": "Anna"}
        ok, cleaned = validate_contact(data)
        assert ok is True
        assert cleaned["name"] == "Anna"
        assert cleaned["phone"] == ""
        assert cleaned["email"] == ""
        assert cleaned["notes"] == ""

    def test_empty_name_rejected(self):
        ok, errors = validate_contact({"name": ""})
        assert ok is False
        assert len(errors) >= 1

    def test_whitespace_name_rejected(self):
        ok, errors = validate_contact({"name": "   "})
        assert ok is False
        assert len(errors) >= 1

    def test_tab_newline_name_rejected(self):
        ok, errors = validate_contact({"name": "\t\n  "})
        assert ok is False
        assert len(errors) >= 1

    def test_missing_name_rejected(self):
        ok, errors = validate_contact({})
        assert ok is False
        assert len(errors) >= 1

    def test_html_tags_stripped_from_name(self):
        data = {"name": "<b>Max</b>"}
        ok, cleaned = validate_contact(data)
        assert ok is True
        assert cleaned["name"] == "Max"

    def test_html_tags_stripped_from_all_fields(self):
        data = {
            "name": "<script>alert('x')</script>Max",
            "phone": "<em>123</em>",
            "email": "<a href='x'>a@b.de</a>",
            "notes": "<p>Notiz</p>",
        }
        ok, cleaned = validate_contact(data)
        assert ok is True
        assert "<" not in cleaned["name"]
        assert "<" not in cleaned["phone"]
        assert "<" not in cleaned["email"]
        assert "<" not in cleaned["notes"]

    def test_whitespace_trimmed(self):
        data = {"name": "  Max  ", "phone": " 123 "}
        ok, cleaned = validate_contact(data)
        assert ok is True
        assert cleaned["name"] == "Max"
        assert cleaned["phone"] == "123"

    def test_name_only_html_tags_rejected(self):
        """Name that becomes empty after HTML stripping should be rejected."""
        ok, errors = validate_contact({"name": "<b></b>"})
        assert ok is False

    def test_name_html_tags_with_whitespace_rejected(self):
        ok, errors = validate_contact({"name": "<b>  </b>"})
        assert ok is False


# --- validate_import_json ---


class TestValidateImportJson:
    def test_valid_import(self):
        data = {
            "version": 1,
            "contacts": [{"name": "Max", "phone": "123"}],
        }
        ok, result = validate_import_json(data)
        assert ok is True
        assert result is data

    def test_missing_version(self):
        data = {"contacts": [{"name": "Max"}]}
        ok, errors = validate_import_json(data)
        assert ok is False
        assert any("version" in e for e in errors)

    def test_missing_contacts(self):
        data = {"version": 1}
        ok, errors = validate_import_json(data)
        assert ok is False
        assert any("contacts" in e for e in errors)

    def test_contacts_not_array(self):
        data = {"version": 1, "contacts": "not an array"}
        ok, errors = validate_import_json(data)
        assert ok is False
        assert any("Array" in e for e in errors)

    def test_contact_missing_name(self):
        data = {"version": 1, "contacts": [{"phone": "123"}]}
        ok, errors = validate_import_json(data)
        assert ok is False
        assert any("Name" in e for e in errors)

    def test_contact_empty_name(self):
        data = {"version": 1, "contacts": [{"name": ""}]}
        ok, errors = validate_import_json(data)
        assert ok is False

    def test_contact_whitespace_name(self):
        data = {"version": 1, "contacts": [{"name": "   "}]}
        ok, errors = validate_import_json(data)
        assert ok is False

    def test_not_a_dict(self):
        ok, errors = validate_import_json("not a dict")
        assert ok is False
        assert any("Objekt" in e for e in errors)

    def test_contact_not_a_dict(self):
        data = {"version": 1, "contacts": ["not a dict"]}
        ok, errors = validate_import_json(data)
        assert ok is False

    def test_multiple_contacts_one_invalid(self):
        data = {
            "version": 1,
            "contacts": [
                {"name": "Max"},
                {"name": ""},
            ],
        }
        ok, errors = validate_import_json(data)
        assert ok is False
        assert any("Kontakt 2" in e for e in errors)

    def test_missing_both_version_and_contacts(self):
        ok, errors = validate_import_json({})
        assert ok is False
        assert len(errors) >= 2
