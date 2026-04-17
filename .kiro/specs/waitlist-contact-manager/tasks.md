# Implementierungsplan: Wartelisten-Kontaktverwaltung

## Übersicht

Schrittweise Implementierung der Flask-basierten Wartelisten-Kontaktverwaltung mit SQLite-Datenbank, serverseitig gerenderten Jinja2-Templates und System-Tray-Integration. Jeder Schritt baut auf dem vorherigen auf und endet mit lauffähigem, integriertem Code.

## Aufgaben

- [x] 1. Projektstruktur und Datenbankschicht erstellen
  - [x] 1.1 Projektverzeichnis anlegen und `db.py` implementieren
    - Verzeichnisstruktur erstellen: `templates/`, `static/`, `icon.ico` (Platzhalter)
    - `db.py` mit `init_db()`, `get_db()` und CRUD-Funktionen implementieren: `add_contact(name, phone, email, notes)`, `get_all_contacts()`, `get_contact(id)`, `update_contact(id, name, phone, email, notes)`, `delete_contact(id)`, `get_visible_contacts(visibility_days)`, `export_contacts()`, `import_contacts(data, mode)`
    - SQLite-Schema gemäß Design anlegen (Tabelle `contacts` mit `id`, `name`, `phone`, `email`, `notes`, `created_at`)
    - Alle Queries als parametrisierte Queries (`?`-Platzhalter)
    - _Anforderungen: 5.1, 5.2, 5.3, 5.4_

  - [x] 1.2 Property-Test: Kontakt-Persistenz Round-Trip
    - **Property 1: Kontakt-Persistenz Round-Trip**
    - Hypothesis-Test: Für beliebige gültige Kontaktdaten ergibt Speichern und Lesen identische Felder mit gültigem Erstellungsdatum
    - **Validiert: Anforderungen 1.2, 1.5, 5.3**

  - [x] 1.3 Property-Test: Löschung entfernt Kontakt vollständig
    - **Property 7: Löschung entfernt Kontakt vollständig**
    - Hypothesis-Test: Nach Löschung ist der Kontakt nicht mehr in der DB und die Anzahl sinkt um eins
    - **Validiert: Anforderung 4.4**

- [x] 2. Eingabevalidierung implementieren
  - [x] 2.1 `validators.py` implementieren
    - `validate_contact(data)`: Name-Pflichtfeld prüfen (nicht leer, nicht nur Whitespace), HTML-Tags entfernen, Felder trimmen
    - `validate_import_json(data)`: JSON-Struktur prüfen (`version`, `contacts`-Array, Pflichtfeld `name` pro Eintrag)
    - Rückgabe: Tuple `(is_valid, cleaned_data_or_errors)`
    - _Anforderungen: 1.4, 1.5, 6.3_

  - [x] 2.2 Property-Test: Whitespace-Namen werden abgelehnt
    - **Property 2: Whitespace-Namen werden abgelehnt**
    - Hypothesis-Test: Strings aus nur Whitespace-Zeichen werden von der Validierung abgelehnt
    - **Validiert: Anforderung 1.4**

- [x] 3. Flask-App und Routes erstellen
  - [x] 3.1 `app.py` mit Flask-Konfiguration und allen Routes implementieren
    - Flask-App erstellen mit Secret Key, Template-Ordner, `VISIBILITY_DAYS = 28`
    - Route `GET /`: Kontaktliste anzeigen (sichtbare oder alle Kontakte je nach `?show_hidden=1`), Wartedauer in Tagen berechnen, Sortierung nach Erstellungsdatum (älteste zuerst), Hinweistext bei leerer Liste
    - Route `POST /add`: Kontakt validieren und speichern, bei Fehler Fehlermeldung anzeigen, bei Erfolg Formular leeren und Redirect
    - Route `GET /edit/<id>`: Kontaktdaten laden und in Eingabemaske anzeigen (404 bei ungültiger ID)
    - Route `POST /edit/<id>`: Bearbeiteten Kontakt validieren und aktualisieren
    - Route `POST /delete/<id>`: Kontakt löschen (404 bei ungültiger ID)
    - Route `GET /export`: Alle Kontakte als JSON-Datei zum Download anbieten
    - Route `GET /import`: Import-Seite anzeigen
    - Route `POST /import`: JSON-Datei importieren mit Modus (ersetzen/zusammenführen)
    - Ausgeblendete Kontakte visuell unterscheidbar markieren (CSS-Klasse `hidden-contact`)
    - _Anforderungen: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 6.1, 6.2, 6.4_

  - [x] 3.2 Property-Test: Korrekte Wartedauer-Berechnung
    - **Property 3: Korrekte Wartedauer-Berechnung**
    - Hypothesis-Test: Für beliebige Erstellungsdaten entspricht die Wartedauer exakt der Tagesdifferenz
    - **Validiert: Anforderung 2.2**

  - [x] 3.3 Property-Test: Sortierung nach Erstellungsdatum
    - **Property 4: Sortierung nach Erstellungsdatum**
    - Hypothesis-Test: Die Kontaktliste ist immer aufsteigend nach Erstellungsdatum sortiert
    - **Validiert: Anforderung 2.3**

  - [x] 3.4 Property-Test: Sichtbarkeitsfilterung bewahrt Datenintegrität
    - **Property 5: Sichtbarkeitsfilterung bewahrt Datenintegrität**
    - Hypothesis-Test: Filterung gibt genau die Kontakte innerhalb der Frist zurück, alle bleiben in der DB
    - **Validiert: Anforderungen 3.1, 3.2**

  - [x] 3.5 Property-Test: Update-Persistenz
    - **Property 6: Update-Persistenz**
    - Hypothesis-Test: Nach Update enthält die DB die neuen Werte, Erstellungsdatum bleibt unverändert
    - **Validiert: Anforderung 4.2**

- [x] 4. Zwischenprüfung – Sicherstellen, dass alle Tests bestehen
  - Sicherstellen, dass alle Tests bestehen, den Anwender bei Fragen konsultieren.

- [x] 5. Jinja2-Templates und Frontend erstellen
  - [x] 5.1 `templates/base.html` – Basis-Template mit Layout
    - Deutschsprachiges HTML-Grundgerüst mit responsivem Layout
    - Navigation, Flash-Messages-Bereich, Content-Block
    - Einbindung von `style.css` und `script.js`
    - _Anforderungen: 7.7, 7.8_

  - [x] 5.2 `templates/index.html` – Kontaktliste und Eingabemaske
    - Eingabemaske mit Feldern: Name (Pflicht), Telefonnummer, E-Mail, Notizen
    - Tabellarische Kontaktliste mit Spalten: Name, Telefonnummer, E-Mail, Notizen, Erstellungsdatum, Wartedauer
    - Bearbeiten-Link pro Kontakt, Löschen-Button mit Bestätigungsdialog
    - Toggle "Ausgeblendete Kontakte anzeigen"
    - Hinweistext bei leerer Liste
    - Ausgeblendete Kontakte mit CSS-Klasse `hidden-contact` visuell unterscheidbar
    - Export-Button, Import-Link
    - _Anforderungen: 1.1, 2.1, 2.4, 3.3, 3.4, 4.1, 4.3, 6.1_

  - [x] 5.3 `templates/import.html` – Import-Dialog
    - Datei-Upload-Feld für JSON-Datei
    - Modus-Auswahl: Ersetzen oder Zusammenführen
    - Fehlermeldungen bei ungültigem Import
    - _Anforderungen: 6.2, 6.3, 6.4_

  - [x] 5.4 `static/style.css` – Styling
    - Responsives Layout (Desktop und Tablet)
    - Styling für Kontaktliste, Eingabemaske, Fehlermeldungen
    - Visuell unterscheidbare Darstellung für ausgeblendete Kontakte (`.hidden-contact`)
    - _Anforderungen: 3.4, 7.8_

  - [x] 5.5 `static/script.js` – Minimales JavaScript
    - Bestätigungsdialog vor Löschung (`confirm()`)
    - Toggle-Logik für "Ausgeblendete Kontakte anzeigen"
    - _Anforderungen: 4.3, 3.3_

- [x] 6. Export/Import-Funktionalität vervollständigen
  - [x] 6.1 Export- und Import-Logik in `db.py` finalisieren
    - `export_contacts()`: Alle Kontakte als JSON-Dict mit `version`, `exported_at`, `contacts`-Array (ohne `id`)
    - `import_contacts(data, mode)`: Bei Modus "ersetzen" alle bestehenden Kontakte löschen, dann importieren; bei "zusammenführen" nur hinzufügen
    - Validierung der Import-Daten über `validators.py`
    - _Anforderungen: 6.1, 6.2, 6.4, 6.5_

  - [x] 6.2 Property-Test: Export/Import Round-Trip
    - **Property 8: Export/Import Round-Trip**
    - Hypothesis-Test: Exportieren und Importieren (Ersetzen-Modus) ergibt identische Kontaktliste
    - **Validiert: Anforderung 6.5**

- [x] 7. Zwischenprüfung – Sicherstellen, dass alle Tests bestehen
  - Sicherstellen, dass alle Tests bestehen, den Anwender bei Fragen konsultieren.

- [x] 8. System-Tray und Einstiegspunkt implementieren
  - [x] 8.1 `tray.py` implementieren
    - pystray-Tray-Icon mit Menü: "Im Browser öffnen", "Beenden"
    - Plattformunabhängige Abstraktion
    - _Anforderungen: 7.3, 7.4, 7.5_

  - [x] 8.2 `main.py` implementieren
    - Flask-Server in separatem Thread starten (ohne sichtbares Konsolenfenster)
    - Tray-Icon im Hauptthread starten
    - Standard-Browser automatisch öffnen
    - Sauberes Herunterfahren bei "Beenden"
    - _Anforderungen: 7.2, 7.3, 7.4, 7.5, 7.6_

- [x] 9. PyInstaller-Build-Konfiguration erstellen
  - [x] 9.1 `build.spec` für PyInstaller erstellen
    - Konfiguration für `--onefile --noconsole`
    - Templates, Static-Dateien und Icon einbinden
    - Plattformunabhängiger Python-Code, Build-Ziel Windows (.exe)
    - _Anforderungen: 7.1, 7.9_

- [x] 10. Unit-Tests für UI und Edge Cases
  - [x] 10.1 Beispielbasierte Unit-Tests schreiben
    - `test_form_has_required_fields`: Eingabemaske enthält alle Felder (Anf. 1.1)
    - `test_empty_list_shows_hint`: Leere Liste zeigt Hinweistext (Anf. 2.4)
    - `test_hidden_contacts_toggle`: Toggle zeigt ausgeblendete Kontakte (Anf. 3.3)
    - `test_hidden_contacts_visual_distinction`: Ausgeblendete Kontakte haben CSS-Klasse (Anf. 3.4)
    - `test_edit_loads_contact_data`: Edit-Route zeigt Kontaktdaten (Anf. 4.1)
    - `test_delete_confirmation`: Lösch-Button hat Bestätigungsdialog (Anf. 4.3)
    - `test_invalid_json_import_rejected`: Ungültiges JSON wird abgelehnt (Anf. 6.3)
    - `test_import_mode_selection`: Import-Seite zeigt Modus-Auswahl (Anf. 6.4)
    - `test_german_ui_labels`: UI-Texte sind auf Deutsch (Anf. 7.7)
    - _Anforderungen: 1.1, 2.4, 3.3, 3.4, 4.1, 4.3, 6.3, 6.4, 7.7_

- [x] 11. Abschlussprüfung – Sicherstellen, dass alle Tests bestehen
  - Sicherstellen, dass alle Tests bestehen, den Anwender bei Fragen konsultieren.

## Hinweise

- Aufgaben mit `*` sind optional und können für ein schnelleres MVP übersprungen werden
- Jede Aufgabe referenziert spezifische Anforderungen zur Nachverfolgbarkeit
- Zwischenprüfungen stellen inkrementelle Validierung sicher
- Property-Tests validieren universelle Korrektheitseigenschaften
- Unit-Tests validieren spezifische Beispiele und Edge Cases
