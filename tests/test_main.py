"""Tests für main.py – Einstiegspunkt der Anwendung.

Testet die Orchestrierung von Flask-Server, Browser-Öffnung und Tray-Icon
ohne tatsächliches Starten von Server oder Display.
"""

from unittest.mock import MagicMock, patch, call

import main


class TestConstants:
    """Tests für die Konfigurationskonstanten."""

    def test_host_is_localhost(self):
        """Server bindet an localhost."""
        assert main.HOST == "127.0.0.1"

    def test_port_is_defined(self):
        """Port ist definiert."""
        assert isinstance(main.PORT, int)
        assert main.PORT > 0

    def test_url_matches_host_port(self):
        """URL stimmt mit Host und Port überein."""
        assert main.URL == f"http://{main.HOST}:{main.PORT}"


class TestStartServer:
    """Tests für start_server."""

    @patch("main.app")
    def test_runs_flask_app(self, mock_app):
        """start_server ruft app.run mit korrekten Parametern auf."""
        main.start_server()
        mock_app.run.assert_called_once_with(
            host=main.HOST, port=main.PORT, use_reloader=False
        )


class TestOpenBrowser:
    """Tests für open_browser."""

    @patch("main.webbrowser.open")
    def test_opens_correct_url(self, mock_open):
        """open_browser öffnet die korrekte URL."""
        main.open_browser()
        mock_open.assert_called_once_with(main.URL)


class TestQuitApp:
    """Tests für quit_app."""

    @patch("main.os._exit")
    def test_calls_os_exit(self, mock_exit):
        """quit_app ruft os._exit(0) auf."""
        main.quit_app()
        mock_exit.assert_called_once_with(0)


class TestMain:
    """Tests für die main-Funktion."""

    @patch("main.run_tray")
    @patch("main.open_browser")
    @patch("main.threading.Thread")
    def test_starts_server_in_daemon_thread(self, mock_thread_cls, mock_browser, mock_tray):
        """Server wird in einem Daemon-Thread gestartet."""
        mock_thread = MagicMock()
        mock_thread_cls.return_value = mock_thread

        main.main()

        mock_thread_cls.assert_called_once_with(target=main.start_server, daemon=True)
        mock_thread.start.assert_called_once()

    @patch("main.run_tray")
    @patch("main.open_browser")
    @patch("main.threading.Thread")
    def test_opens_browser(self, mock_thread_cls, mock_browser, mock_tray):
        """Browser wird nach Server-Start geöffnet."""
        mock_thread_cls.return_value = MagicMock()

        main.main()

        mock_browser.assert_called_once()

    @patch("main.run_tray")
    @patch("main.open_browser")
    @patch("main.threading.Thread")
    def test_starts_tray_with_callbacks(self, mock_thread_cls, mock_browser, mock_tray):
        """Tray-Icon wird mit korrekten Callbacks gestartet."""
        mock_thread_cls.return_value = MagicMock()

        main.main()

        mock_tray.assert_called_once_with(
            open_browser_callback=main.open_browser,
            quit_callback=main.quit_app,
        )

    @patch("main.run_tray")
    @patch("main.open_browser")
    @patch("main.threading.Thread")
    def test_execution_order(self, mock_thread_cls, mock_browser, mock_tray):
        """Reihenfolge: Thread starten → Browser öffnen → Tray starten."""
        mock_thread = MagicMock()
        mock_thread_cls.return_value = mock_thread

        call_order = []
        mock_thread.start.side_effect = lambda: call_order.append("server_start")
        mock_browser.side_effect = lambda: call_order.append("browser_open")
        mock_tray.side_effect = lambda **kw: call_order.append("tray_run")

        main.main()

        assert call_order == ["server_start", "browser_open", "tray_run"]
