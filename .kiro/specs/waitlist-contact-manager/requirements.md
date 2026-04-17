# Anforderungsdokument

## Einleitung

Eine einfache Anwendung zur Verwaltung einer Warteliste mit Kontaktdaten. Die App läuft als leichtgewichtiger lokaler Webserver (Python + Flask) mit SQLite-Datenbank und wird im Browser bedient. Sie wird als eigenständige ausführbare Datei (.exe) ausgeliefert, benötigt keine Installation und keine Internetverbindung. Einträge werden nach einer konfigurierbaren Frist (Standard: 4 Wochen) automatisch ausgeblendet. Es werden einige Einträge pro Woche erwartet.

### Technologie-Empfehlung

Für die Umsetzung wird eine **Python + Flask Anwendung mit SQLite-Datenbank** empfohlen, gebündelt als ausführbare Datei via **PyInstaller**:

- **Keine Installation nötig** – eine einzige `.exe`-Datei, Doppelklick genügt (kein Python, kein Setup)
- **System-Tray-Integration** – die App läuft im Hintergrund mit einem Tray-Icon (via `pystray`), über das der Browser geöffnet oder die App beendet werden kann
- **Primär Windows** – der erste Build zielt auf Windows ab; der Python-Code ist plattformunabhängig, sodass macOS/Linux-Builds später möglich sind
- **Sichere lokale Datenhaltung** – alle Daten werden in einer lokalen SQLite-Datenbankdatei gespeichert
- **Kein externer Server** – Flask läuft lokal im Hintergrund ohne sichtbares Konsolenfenster
- **Bedienung im Browser** – die Benutzeroberfläche wird über den lokalen Browser aufgerufen (serverseitig gerenderte Jinja2-Templates mit einfachem CSS/JS)
- **Export/Import** – Daten können als JSON-Datei exportiert und importiert werden (Backup)

## Glossar

- **App**: Die Wartelisten-Kontaktverwaltung als ausführbare Desktop-Anwendung mit Web-UI
- **Server**: Der lokale Flask-Webserver, der im Hintergrund läuft und die Web-UI bereitstellt
- **Tray-Icon**: Das System-Tray-Symbol, über das der Anwender die App steuern kann (Browser öffnen, App beenden)
- **SQLite-Datenbank**: Die lokale Datenbankdatei, in der alle Kontaktdaten persistent gespeichert werden
- **PyInstaller**: Das Build-Tool, das Python-Code und alle Abhängigkeiten in eine eigenständige `.exe`-Datei bündelt
- **Kontakt**: Ein Eintrag auf der Warteliste mit Name, Telefonnummer, E-Mail und optionalen Notizen
- **Warteliste**: Die Sammlung aller Kontakte mit Erstellungsdatum und Wartedauer
- **Wartedauer**: Die berechnete Zeitspanne zwischen dem Erstellungsdatum eines Kontakts und dem aktuellen Datum
- **Sichtbarkeitsfrist**: Der Zeitraum (Standard: 4 Wochen), nach dem ein Kontakt automatisch ausgeblendet wird
- **Eingabemaske**: Das Formular zur Erfassung neuer Kontaktdaten
- **Kontaktliste**: Die tabellarische Darstellung aller sichtbaren Kontakte

## Anforderungen

### Anforderung 1: Kontakt erfassen

**User Story:** Als Anwender möchte ich Kontaktdaten über eine Eingabemaske erfassen, damit ich neue Personen zur Warteliste hinzufügen kann.

#### Akzeptanzkriterien

1. THE App SHALL eine Eingabemaske mit den Feldern Name, Telefonnummer, E-Mail-Adresse und Notizen anzeigen
2. WHEN der Anwender das Formular absendet, THE App SHALL den Kontakt mit einem automatisch generierten Erstellungsdatum in der SQLite-Datenbank speichern
3. WHEN der Anwender das Formular absendet, THE App SHALL die Eingabemaske nach erfolgreicher Speicherung leeren
4. IF das Feld Name leer ist, THEN THE App SHALL eine Fehlermeldung anzeigen und den Kontakt nicht speichern
5. THE App SHALL das Feld Name als Pflichtfeld und die Felder Telefonnummer, E-Mail-Adresse und Notizen als optionale Felder behandeln

### Anforderung 2: Warteliste anzeigen

**User Story:** Als Anwender möchte ich die Warteliste mit allen sichtbaren Kontakten und deren Wartedauer sehen, damit ich einen Überblick über die wartenden Personen habe.

#### Akzeptanzkriterien

1. THE App SHALL alle sichtbaren Kontakte in einer tabellarischen Kontaktliste mit den Spalten Name, Telefonnummer, E-Mail-Adresse, Notizen, Erstellungsdatum und Wartedauer anzeigen
2. THE App SHALL die Wartedauer jedes Kontakts in Tagen berechnen und anzeigen (Differenz zwischen aktuellem Datum und Erstellungsdatum)
3. THE App SHALL die Kontaktliste nach Erstellungsdatum sortieren, wobei der älteste Kontakt zuerst angezeigt wird
4. WHEN die Warteliste keine sichtbaren Kontakte enthält, THE App SHALL einen Hinweistext anzeigen, dass die Warteliste leer ist

### Anforderung 3: Automatisches Ausblenden nach Sichtbarkeitsfrist

**User Story:** Als Anwender möchte ich, dass Kontakte nach 4 Wochen automatisch ausgeblendet werden, damit die Warteliste übersichtlich bleibt.

#### Akzeptanzkriterien

1. THE App SHALL Kontakte, deren Erstellungsdatum länger als die Sichtbarkeitsfrist (Standard: 28 Tage) zurückliegt, in der Kontaktliste ausblenden
2. THE App SHALL ausgeblendete Kontakte nicht aus der SQLite-Datenbank löschen, sondern nur in der Kontaktliste verbergen
3. WHEN der Anwender die Option "Ausgeblendete Kontakte anzeigen" aktiviert, THE App SHALL alle Kontakte einschließlich der ausgeblendeten anzeigen
4. THE App SHALL ausgeblendete Kontakte in der Kontaktliste visuell von sichtbaren Kontakten unterscheidbar darstellen

### Anforderung 4: Kontakt bearbeiten und löschen

**User Story:** Als Anwender möchte ich bestehende Kontakte bearbeiten oder löschen können, damit ich die Warteliste aktuell halten kann.

#### Akzeptanzkriterien

1. WHEN der Anwender auf einen Kontakt in der Kontaktliste klickt, THE App SHALL die Kontaktdaten in der Eingabemaske zum Bearbeiten anzeigen
2. WHEN der Anwender die Bearbeitung speichert, THE App SHALL die geänderten Kontaktdaten in der SQLite-Datenbank aktualisieren
3. WHEN der Anwender einen Kontakt löschen möchte, THE App SHALL eine Bestätigungsabfrage anzeigen, bevor der Kontakt endgültig entfernt wird
4. WHEN der Anwender die Löschung bestätigt, THE App SHALL den Kontakt dauerhaft aus der SQLite-Datenbank entfernen

### Anforderung 5: Lokale Datenpersistenz mit SQLite

**User Story:** Als Anwender möchte ich, dass meine Daten sicher in einer lokalen Datenbankdatei gespeichert werden, damit ich keine Daten verliere und die Daten unabhängig vom Browser erhalten bleiben.

#### Akzeptanzkriterien

1. THE App SHALL alle Kontaktdaten in einer lokalen SQLite-Datenbankdatei speichern
2. WHEN der Server gestartet wird, THE App SHALL die SQLite-Datenbank initialisieren und das Kontakte-Schema anlegen, falls die Datenbank noch nicht existiert
3. WHEN ein Kontakt hinzugefügt, bearbeitet oder gelöscht wird, THE App SHALL die Änderung sofort in der SQLite-Datenbank persistieren
4. THE App SHALL die SQLite-Datenbankdatei im Anwendungsverzeichnis ablegen, sodass der Anwender die Datei einfach sichern oder kopieren kann

### Anforderung 6: Daten exportieren und importieren

**User Story:** Als Anwender möchte ich meine Warteliste als Datei exportieren und importieren können, damit ich ein Backup erstellen oder die Daten auf einen anderen Rechner übertragen kann.

#### Akzeptanzkriterien

1. WHEN der Anwender den Export auslöst, THE App SHALL alle Kontaktdaten (einschließlich ausgeblendeter Kontakte) aus der SQLite-Datenbank als JSON-Datei zum Download anbieten
2. WHEN der Anwender eine JSON-Datei importiert, THE App SHALL die enthaltenen Kontaktdaten in die SQLite-Datenbank laden
3. IF die importierte Datei kein gültiges JSON-Format hat, THEN THE App SHALL eine Fehlermeldung anzeigen und den Import abbrechen
4. WHEN der Anwender einen Import durchführt, THE App SHALL den Anwender fragen, ob die bestehenden Daten ersetzt oder mit den importierten Daten zusammengeführt werden sollen
5. FOR ALL gültige Kontaktdaten-Objekte, Exportieren dann Importieren (mit Ersetzen) SHALL eine identische Warteliste erzeugen (Round-Trip-Eigenschaft)

### Anforderung 7: Einfache Installation und Bedienung

**User Story:** Als Anwender möchte ich die App ohne technische Kenntnisse per Doppelklick starten können, damit ich sofort mit der Warteliste arbeiten kann.

#### Akzeptanzkriterien

1. THE App SHALL als einzelne ausführbare Datei (.exe für Windows) ausgeliefert werden, die ohne Installation und ohne vorinstalliertes Python lauffähig ist
2. WHEN der Anwender die .exe-Datei startet, THE App SHALL den lokalen Flask-Server im Hintergrund starten (ohne sichtbares Konsolenfenster) und automatisch den Standard-Browser mit der App-URL öffnen
3. THE App SHALL ein System-Tray-Icon anzeigen, über das der Anwender den Browser erneut öffnen oder die App beenden kann
4. WHEN der Anwender den Browser-Tab schließt, THE App SHALL im Hintergrund weiterlaufen, bis der Anwender die App über das Tray-Icon beendet
5. WHEN der Anwender "Beenden" im Tray-Menü wählt, THE App SHALL den Flask-Server sauber herunterfahren und den Prozess beenden
6. THE App SHALL ohne Internetverbindung vollständig funktionsfähig sein
7. THE App SHALL eine deutschsprachige Benutzeroberfläche bereitstellen
8. THE App SHALL ein responsives Layout verwenden, das auf Desktop- und Tablet-Bildschirmen nutzbar ist
9. THE App SHALL mit PyInstaller (`--noconsole`) gebaut werden, wobei der Python-Code plattformunabhängig bleibt, um spätere macOS/Linux-Builds zu ermöglichen
