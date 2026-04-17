"""Tests für tray.py – System-Tray-Integration.

Testet die plattformunabhängige Tray-Logik ohne tatsächliches Display.
"""

import os
from unittest.mock import MagicMock, patch

import pystray
from PIL import Image

from src import tray


class TestLoadIcon:
    """Tests für das Laden des Tray-Icons."""

    def test_fallback_icon_when_file_missing(self, tmp_path, monkeypatch):
        """Fallback-Icon wird erzeugt, wenn icon.ico nicht existiert."""
        monkeypatch.setattr(tray, "_get_app_dir", lambda: str(tmp_path))
        icon = tray.load_icon()
        assert isinstance(icon, Image.Image)
        assert icon.size[0] > 0
        assert icon.size[1] > 0

    def test_fallback_icon_when_file_invalid(self, tmp_path, monkeypatch):
        """Fallback-Icon wird erzeugt, wenn icon.ico keine gültige Bilddatei ist."""
        monkeypatch.setattr(tray, "_get_app_dir", lambda: str(tmp_path))
        invalid_icon = tmp_path / "icon.ico"
        invalid_icon.write_text("not an image")
        icon = tray.load_icon()
        assert isinstance(icon, Image.Image)

    def test_loads_valid_icon(self, tmp_path, monkeypatch):
        """Gültige icon.ico wird geladen."""
        monkeypatch.setattr(tray, "_get_app_dir", lambda: str(tmp_path))
        # Erstelle eine gültige ICO-Datei
        img = Image.new("RGBA", (32, 32), (255, 0, 0, 255))
        icon_path = tmp_path / "icon.ico"
        img.save(str(icon_path), format="ICO")
        icon = tray.load_icon()
        assert isinstance(icon, Image.Image)


class TestCreateFallbackIcon:
    """Tests für die Fallback-Icon-Erzeugung."""

    def test_default_size(self):
        """Fallback-Icon hat die Standard-Größe 64x64."""
        icon = tray._create_fallback_icon()
        assert icon.size == (64, 64)

    def test_custom_size(self):
        """Fallback-Icon kann mit benutzerdefinierter Größe erzeugt werden."""
        icon = tray._create_fallback_icon(size=128)
        assert icon.size == (128, 128)

    def test_rgba_mode(self):
        """Fallback-Icon ist im RGBA-Modus."""
        icon = tray._create_fallback_icon()
        assert icon.mode == "RGBA"


class TestRunTray:
    """Tests für die run_tray-Funktion."""

    @patch("src.tray.pystray.Icon")
    def test_creates_icon_with_correct_name(self, mock_icon_class):
        """Tray-Icon wird mit korrektem Namen erstellt."""
        mock_icon_instance = MagicMock()
        mock_icon_class.return_value = mock_icon_instance

        img = Image.new("RGBA", (32, 32), (0, 0, 0, 255))
        tray.run_tray(
            open_browser_callback=lambda: None,
            quit_callback=lambda: None,
            icon_image=img,
        )

        mock_icon_class.assert_called_once()
        call_kwargs = mock_icon_class.call_args
        assert call_kwargs[1]["name"] == "waitlist-contact-manager"
        assert call_kwargs[1]["title"] == "Wartelisten-Kontaktverwaltung"
        mock_icon_instance.run.assert_called_once()

    @patch("src.tray.pystray.Icon")
    def test_menu_has_two_items(self, mock_icon_class):
        """Tray-Menü hat genau zwei Einträge."""
        mock_icon_instance = MagicMock()
        mock_icon_class.return_value = mock_icon_instance

        img = Image.new("RGBA", (32, 32), (0, 0, 0, 255))
        tray.run_tray(
            open_browser_callback=lambda: None,
            quit_callback=lambda: None,
            icon_image=img,
        )

        call_kwargs = mock_icon_class.call_args
        menu = call_kwargs[1]["menu"]
        # pystray.Menu items
        items = list(menu)
        assert len(items) == 2

    @patch("src.tray.pystray.Icon")
    def test_menu_labels_german(self, mock_icon_class):
        """Menüeinträge sind auf Deutsch."""
        mock_icon_instance = MagicMock()
        mock_icon_class.return_value = mock_icon_instance

        img = Image.new("RGBA", (32, 32), (0, 0, 0, 255))
        tray.run_tray(
            open_browser_callback=lambda: None,
            quit_callback=lambda: None,
            icon_image=img,
        )

        call_kwargs = mock_icon_class.call_args
        menu = call_kwargs[1]["menu"]
        items = list(menu)
        # MenuItem text attribute
        assert str(items[0]) == "Im Browser öffnen"
        assert str(items[1]) == "Beenden"

    @patch("src.tray.pystray.Icon")
    def test_open_browser_callback_invoked(self, mock_icon_class):
        """'Im Browser öffnen' ruft den open_browser_callback auf."""
        mock_icon_instance = MagicMock()
        mock_icon_class.return_value = mock_icon_instance

        callback = MagicMock()
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 255))
        tray.run_tray(
            open_browser_callback=callback,
            quit_callback=lambda: None,
            icon_image=img,
        )

        call_kwargs = mock_icon_class.call_args
        menu = call_kwargs[1]["menu"]
        items = list(menu)
        # Trigger the first menu item's action
        action = items[0]._action
        action()
        callback.assert_called_once()

    @patch("src.tray.pystray.Icon")
    def test_quit_callback_invoked(self, mock_icon_class):
        """'Beenden' ruft den quit_callback auf."""
        mock_icon_instance = MagicMock()
        mock_icon_class.return_value = mock_icon_instance

        callback = MagicMock()
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 255))
        tray.run_tray(
            open_browser_callback=lambda: None,
            quit_callback=callback,
            icon_image=img,
        )

        call_kwargs = mock_icon_class.call_args
        menu = call_kwargs[1]["menu"]
        items = list(menu)
        # Trigger the second menu item's action (Beenden)
        action = items[1]._action
        action()
        callback.assert_called_once()

    @patch("src.tray.load_icon")
    @patch("src.tray.pystray.Icon")
    def test_uses_load_icon_when_no_image_provided(self, mock_icon_class, mock_load):
        """Wenn kein icon_image übergeben wird, wird load_icon() aufgerufen."""
        mock_icon_instance = MagicMock()
        mock_icon_class.return_value = mock_icon_instance
        mock_load.return_value = Image.new("RGBA", (32, 32), (0, 0, 0, 255))

        tray.run_tray(
            open_browser_callback=lambda: None,
            quit_callback=lambda: None,
        )

        mock_load.assert_called_once()


class TestGetAppDir:
    """Tests für _get_app_dir."""

    def test_returns_directory_string(self):
        """_get_app_dir gibt einen existierenden Verzeichnispfad zurück."""
        result = tray._get_app_dir()
        assert isinstance(result, str)
        assert os.path.isdir(result)
