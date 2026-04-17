"""System-Tray-Integration für die Wartelisten-Kontaktverwaltung.

Erstellt ein plattformunabhängiges Tray-Icon mit Menü über pystray.
Menüpunkte: "Im Browser öffnen" und "Beenden".
"""

import os
import sys
from typing import Callable, Optional

from PIL import Image, ImageDraw

try:
    import pystray
except Exception:
    pystray = None  # type: ignore[assignment]


def _get_app_dir() -> str:
    """Gibt das Anwendungsverzeichnis zurück (PyInstaller-kompatibel)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _create_fallback_icon(size: int = 64) -> Image.Image:
    """Erzeugt ein einfaches Fallback-Icon (blauer Kreis auf weißem Grund)."""
    image = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    margin = size // 8
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill=(52, 120, 198, 255),
    )
    return image


def load_icon() -> Image.Image:
    """Lädt icon.ico aus dem App-Verzeichnis oder erzeugt ein Fallback-Icon."""
    icon_path = os.path.join(_get_app_dir(), "icon.ico")
    try:
        return Image.open(icon_path)
    except Exception:
        return _create_fallback_icon()


def run_tray(
    open_browser_callback: Callable[[], None],
    quit_callback: Callable[[], None],
    icon_image: Optional[Image.Image] = None,
) -> None:
    """Startet das System-Tray-Icon mit Menü.

    Args:
        open_browser_callback: Wird aufgerufen bei "Im Browser öffnen".
        quit_callback: Wird aufgerufen bei "Beenden".
        icon_image: Optionales Icon-Bild. Falls None, wird load_icon() verwendet.
    """
    if icon_image is None:
        icon_image = load_icon()

    menu = pystray.Menu(
        pystray.MenuItem("Im Browser öffnen", lambda: open_browser_callback()),
        pystray.MenuItem("Beenden", lambda: _quit(quit_callback)),
    )

    icon = pystray.Icon(
        name="waitlist-contact-manager",
        icon=icon_image,
        title="Wartelisten-Kontaktverwaltung",
        menu=menu,
    )

    icon.run()


def _quit(quit_callback: Callable[[], None]) -> None:
    """Ruft den Quit-Callback auf."""
    quit_callback()
