Hier ist eine ausführliche README.md für meinen Vokabeltrainer-Programm mit espeak für die Sprachausgabe:
# Vokabeltrainer

Ein einfacher Vokabeltrainer mit GUI in Python (Tkinter), der englische Wörter abfragt und die passenden deutschen Übersetzungen animiert anzeigt. Die Anwendung verwendet eine SQLite-Datenbank zur Speicherung der Vokabeln.

## Features

- Vokabeln hinzufügen, löschen und verwalten
- Import von Vokabeln aus CSV-Dateien
- Zufällige Abfrage von Vokabeln mit animierten Antwortmöglichkeiten
- Sprachausgabe des englischen Wortes (mit `espeak`)
- Punktestand als "Sterne" angezeigt

## Voraussetzungen

- Python 3.x
- Tkinter (meist vorinstalliert bei Python)
- SQLite3 (in Python integriert)
- `espeak` für die Sprachausgabe (muss separat installiert sein)

## Installation von `espeak`

Auf Debian/Ubuntu-Systemen:

```bash
sudo apt update
sudo apt install espeak
Für andere Linux-Distributionen bitte den passenden Paketmanager verwenden.
Installation der Python-Abhängigkeiten
Alle genutzten Bibliotheken sind Standard bei Python (tkinter, sqlite3, csv, subprocess), daher keine weiteren Python-Pakete notwendig.
Dateien
    • vokabeltrainer.py – Hauptprogramm
    • vokabeln.db – SQLite-Datenbank (wird beim ersten Start automatisch angelegt)
Nutzung
    1. Starte das Programm:
python3 vokabeltrainer.py
    2. Im oberen Bereich kannst du neue Vokabeln (Englisch und Deutsch) hinzufügen.
    3. Mit dem Button "Liste aktualisieren" kannst du die gespeicherten Vokabeln in der Liste sehen.
    4. Du kannst Vokabeln löschen oder per CSV importieren.
    5. Im unteren Bereich kannst du eine Übungsrunde starten. Dort werden animiert mehrere deutsche Übersetzungen angezeigt.
    6. Klicke auf die richtige Übersetzung, um Punkte zu sammeln.
    7. Über den Button „Englisches Wort sprechen“ kannst du dir das englische Wort per espeak vorlesen lassen.
Datenbank
Die SQLite-Datenbank vokabeln.db wird automatisch im Programmverzeichnis erstellt, falls nicht vorhanden.
CSV-Import
CSV-Dateien müssen mindestens zwei Spalten haben: Englisch und Deutsch.
Beispiel:
apple,Apfel
dog,Hund
Sprachausgabe
Die Sprachausgabe nutzt das Linux-Tool espeak mit englischer Stimme.
Stelle sicher, dass espeak installiert und in deinem PATH verfügbar ist.
Lizenz
Dieses Projekt ist Open Source. Du kannst den Code frei verwenden und anpassen.

Viel Erfolg beim Lernen!
Bei Fragen oder Problemen gerne melden.

Erstellt von sbgh2025
Letzte Aktualisierung: 2025-05-26

---


