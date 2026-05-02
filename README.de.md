<div align="center">

🇧🇷 [Português](README.md) | 🇺🇸 [English](README.en.md) | 🇪🇸 [Español](README.es.md) | 🇩🇪 [Deutsch](README.de.md)

</div>

<br>

<div align="center">

# ⚡ QueryFacil

**Desktop-Anwendung zur Optimierung und Verwaltung von SQL-Abfragen mit einer intuitiven grafischen Oberfläche.**

Verbinden Sie sich mit PostgreSQL, führen Sie Queries aus, speichern Sie Ihre Favoriten und exportieren Sie Ergebnisse nach Excel — alles an einem Ort.

![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-41CD52?logo=qt&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Connected-336791?logo=postgresql&logoColor=white)
![License MIT](https://img.shields.io/badge/License-MIT-green.svg)

![Desktop App](https://img.shields.io/badge/Type-Desktop_Application-informational)
![Cross Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-orange)
![SQLite Local](https://img.shields.io/badge/Storage-Local_SQLite-critical)

</div>

<br>

## 📸 Benutzeroberfläche

```
┌──────────────────────────────────────────────────────────────────────────┐
│  SQL-Berichtsgenerator                                    ─  □  X       │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─── Verbindungsverwaltung ─────────────────────────────────────────┐  │
│  │ Verbindung: [▼ Produktion DB   ] [Verbindung hinzufügen] [Mgmt]  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─── SQL-Abfrage ───────────────────────────────────────────────────┐  │
│  │ Gespeichert: [▼ Kunden nach Bund ] [Aktuelle speichern] [Mgmt]   │  │
│  │ ┌────────────────────────────────────────────────────────────────┐ │  │
│  │ │ SELECT name, stadt, bundesland                                │ │  │
│  │ │ FROM kunden                                                   │ │  │
│  │ │ WHERE bundesland = 'CE'                                       │ │  │
│  │ │ ORDER BY name;                                                │ │  │
│  │ └────────────────────────────────────────────────────────────────┘ │  │
│  │                              [ ▶  Abfrage ausführen             ]  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─── Exportoptionen ────────────────────────────────────────────────┐  │
│  │ [✓] Excel (XLSX)    Ausgabe: relatorios_gerados/                  │  │
│  │ Berichtsname: [ kunden_ceara   ]  [ 📥 Letzte Ergebnisse Exp.  ] │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─── Protokolle und Ergebnisse ────────────────────────────────────┐  │
│  │ 2026-01-15 10:32 - INFO - Verbunden mit: Produktion DB          │  │
│  │ 2026-01-15 10:32 - INFO - SELECT erfolgreich ausgeführt.        │  │
│  │       name            stadt          bundesland                   │  │
│  │  ─────────────────────────────────────────────────                │  │
│  │  Ana Silva         Fortaleza       CE                            │  │
│  │  Carlos Souza      Sobral         CE                             │  │
│  │  ... (148 weitere Zeilen. Exportieren für alle.)                 │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

<br>

## ✅ Funktionen

| Funktion | Details |
|----------|---------|
| ✅ **Mehrere Verbindungen** | Mehrere PostgreSQL-Verbindungen hinzufügen, bearbeiten und verwalten |
| ✅ **Verbindungstest** | Verbindungen vor dem Speichern validieren |
| ✅ **Integrierter SQL-Editor** | Queries direkt in der Benutzeroberfläche schreiben und ausführen |
| ✅ **Gespeicherte Queries** | Ihre am häufigsten verwendeten Queries speichern, laden und verwalten |
| ✅ **Excel-Export** | `.xlsx`-Berichte mit automatisch angepassten Spalten generieren |
| ✅ **LATIN1-Unterstützung** | Kompatibel mit LATIN1/UTF-8-kodierten Datenbanken |
| ✅ **Echtzeit-Protokollierung** | Protokolle direkt in der Anwendung anzeigen |
| ✅ **Lokale Speicherung** | Alles in SQLite gespeichert — keine Cloud-Abhängigkeit |
| ✅ **Plattformübergreifend** | Funktioniert auf Windows, Linux und macOS |

<br>

## 🛠 Technologien

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI_5.15%2B-41CD52?logo=qt&logoColor=white)
![psycopg2](https://img.shields.io/badge/psycopg2-binary-PostgreSQL_Treiber-336791?logo=postgresql&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-Datenmanipulation-150458?logo=pandas&logoColor=white)
![openpyxl](https://img.shields.io/badge/openpyxl-Excel_Generierung-217346?logo=openxml&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Lokale_Speicherung-003B57?logo=sqlite&logoColor=white)

<br>

## 🏗 Architektur

```
┌─────────────────────────────────────────────────────┐
│                   MainWindow (PyQt5)                 │
│                    QMainWindow                      │
├──────────┬──────────────┬───────────────────────────┤
│ Connection│  SQL Query   │  Report Output            │
│  Dialogs  │   Editor     │  (Excel Export)           │
├──────────┴──────┬───────┴───────────────────────────┤
│                 ▼                                   │
│           ┌───────────┐                             │
│           │ DBManager │  ← psycopg2 → PostgreSQL    │
│           │  (Core)   │  ← sqlite3 → Lokale Config  │
│           └─────┬─────┘                             │
│                 ▼                                   │
│     ┌────────────────────┐                          │
│     │ ReportGenerator    │  → pandas + openpyxl     │
│     └────────────────────┘     → .xlsx Dateien      │
└─────────────────────────────────────────────────────┘
```

<br>

## 📦 Installation

### Voraussetzungen

- Python 3.8 oder höher
- Zugängliche PostgreSQL-Instanz (lokal oder remote)

### Schritt für Schritt

```bash
# 1. Repository klonen
git clone https://github.com/amonmelo/QueryFacil.git
cd QueryFacil

# 2. (Optional) Virtuelle Umgebung erstellen
python -m venv venv

# Aktivieren
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Anwendung starten
python app_completo.py
```

<br>

## 🚀 Verwendung

### 1. Verbindung hinzufügen

Klicken Sie auf **Verbindung hinzufügen**, füllen Sie die Datenbankzugangsdaten aus und testen Sie die Verbindung:

```
Host: 192.168.1.100
Port: 5432
Database: meine_datenbank
User: postgres
Password: ********
```

### 2. Query ausführen

Wählen Sie eine Verbindung im Dropdown, schreiben Sie Ihr SQL und klicken Sie auf **Abfrage ausführen**:

```sql
SELECT name, stadt, bundesland
FROM kunden
WHERE bundesland = 'CE'
ORDER BY name;
```

### 3. Favoriten-Query speichern

Klicken Sie nach dem Schreiben einer Query auf **Aktuelle Query speichern** und geben Sie ihr einen Namen.

### 4. Nach Excel exportieren

Füllen Sie nach Ausführung einer `SELECT`-Abfrage den Berichtsnamen aus und klicken Sie auf **Letzte Ergebnisse exportieren**. Die Datei wird in `relatorios_gerados/` gespeichert.

<br>

## 🗺 Roadmap

| Funktion | Status |
|----------|--------|
| Syntax-Highlighting im SQL-Editor | 🔜 Geplant |
| Ergebnistabelle mit `QTableView` | 🔜 Geplant |
| Asynchrone Ausführung (Threading) | 🔜 Geplant |
| CSV- und PDF-Export | 🔜 Geplant |
| Ausführungsverlauf von Queries | 🔜 Geplant |
| Dunkler Modus | 💡 Idee |
| Passwortverschlüsselung | 💡 Idee |

<br>

## 🤝 Mitwirken

Beiträge sind willkommen! Öffnen Sie gerne ein Issue oder reichen Sie einen Pull Request ein. So starten Sie:

1. Forken Sie das Projekt
2. Erstellen Sie einen Feature-Branch (`git checkout -b feature/mein-feature`)
3. Committen Sie Ihre Änderungen (`git commit -m 'feat: Beschreibung der Änderung'`)
4. Pushen Sie zum Branch (`git push origin feature/mein-feature`)
5. Öffnen Sie einen Pull Request

<br>

## 📄 Lizenz

Dieses Projekt ist unter der [MIT-Lizenz](LICENSE) lizenziert.

<br>

---

<div align="center">

Erstellt mit ☕ und 🐍 von **amonmelo**

<a href="https://www.linkedin.com/in/amonmelo/">![LinkedIn](https://img.shields.io/badge/LinkedIn-amonmelo-0A66C2?logo=linkedin&logoColor=white)</a>
<a href="https://github.com/amonmelo">![GitHub](https://img.shields.io/badge/GitHub-amonmelo-181717?logo=github&logoColor=white)</a>

</div>
