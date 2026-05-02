<div align="center">

🇧🇷 [Português](README.md) | 🇺🇸 [English](README.en.md) | 🇪🇸 [Español](README.es.md) | 🇩🇪 [Deutsch](README.de.md)

</div>

<br>

<div align="center">

# ⚡ QueryFacil

**Desktop tool to optimize and manage SQL queries with an intuitive graphical interface.**

Connect to PostgreSQL, execute queries, save your favorites, and export results to Excel — all in one place.

![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-41CD52?logo=qt&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Connected-336791?logo=postgresql&logoColor=white)
![License MIT](https://img.shields.io/badge/License-MIT-green.svg)

![Desktop App](https://img.shields.io/badge/Type-Desktop_Application-informational)
![Cross Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-orange)
![SQLite Local](https://img.shields.io/badge/Storage-Local_SQLite-critical)

</div>

<br>

## 📸 Interface

```
┌──────────────────────────────────────────────────────────────────────────┐
│  SQL Report Generator                                        ─  □  X   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─── Connection Management ──────────────────────────────────────────┐  │
│  │ Connection: [▼ Production DB    ] [Add Connection] [Manage...]    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─── SQL Query ─────────────────────────────────────────────────────┐  │
│  │ Saved Query: [▼ Clients by State] [Save Current] [Manage...]     │  │
│  │ ┌────────────────────────────────────────────────────────────────┐ │  │
│  │ │ SELECT name, city, state                                      │ │  │
│  │ │ FROM clients                                                  │ │  │
│  │ │ WHERE state = 'CE'                                            │ │  │
│  │ │ ORDER BY name;                                                │ │  │
│  │ └────────────────────────────────────────────────────────────────┘ │  │
│  │                              [ ▶  Execute Query                  ]  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─── Report Output Options ─────────────────────────────────────────┐  │
│  │ [✓] Excel (XLSX)    Output: relatorios_gerados/                   │  │
│  │ Report Name: [ clients_ceara  ]   [ 📥 Export Last Results      ] │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─── Logs and Query Output ─────────────────────────────────────────┐  │
│  │ 2026-01-15 10:32 - INFO - Connected to: Production DB            │  │
│  │ 2026-01-15 10:32 - INFO - SELECT query executed successfully.     │  │
│  │         name             city            state                    │  │
│  │  ─────────────────────────────────────────────────                │  │
│  │  Ana Silva         Fortaleza        CE                           │  │
│  │  Carlos Souza      Sobral          CE                            │  │
│  │  ... (148 more rows. Export to see all.)                         │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

<br>

## ✅ Features

| Feature | Details |
|---------|---------|
| ✅ **Multiple connections** | Add, edit, and manage several PostgreSQL connections |
| ✅ **Connection testing** | Validate connections before saving |
| ✅ **Integrated SQL editor** | Write and execute queries directly in the UI |
| ✅ **Saved queries** | Save, load, and manage your most-used queries |
| ✅ **Excel export** | Generate `.xlsx` reports with auto-adjusted columns |
| ✅ **LATIN1 support** | Compatible with LATIN1/UTF-8 encoded databases |
| ✅ **Real-time logging** | View logs inside the application itself |
| ✅ **Local storage** | Everything saved in SQLite — no cloud dependency |
| ✅ **Cross-platform** | Works on Windows, Linux, and macOS |

<br>

## 🛠 Tech Stack

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI_5.15%2B-41CD52?logo=qt&logoColor=white)
![psycopg2](https://img.shields.io/badge/psycopg2-binary-PostgreSQL_Driver-336791?logo=postgresql&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-Data_Manipulation-150458?logo=pandas&logoColor=white)
![openpyxl](https://img.shields.io/badge/openpyxl-Excel_Generation-217346?logo=openxml&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Local_Storage-003B57?logo=sqlite&logoColor=white)

<br>

## 🏗 Architecture

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
│           │  (Core)   │  ← sqlite3 → Local Config   │
│           └─────┬─────┘                             │
│                 ▼                                   │
│     ┌────────────────────┐                          │
│     │ ReportGenerator    │  → pandas + openpyxl     │
│     └────────────────────┘     → .xlsx files        │
└─────────────────────────────────────────────────────┘
```

<br>

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Accessible PostgreSQL instance (local or remote)

### Step by step

```bash
# 1. Clone the repository
git clone https://github.com/amonmelo/QueryFacil.git
cd QueryFacil

# 2. (Optional) Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app_completo.py
```

<br>

## 🚀 Usage

### 1. Add a connection

Click **Add Connection**, fill in your database credentials, and test the connection:

```
Host: 192.168.1.100
Port: 5432
Database: my_database
User: postgres
Password: ********
```

### 2. Execute a query

Select a connection from the combo box, write your SQL, and click **Execute Query**:

```sql
SELECT name, city, state
FROM clients
WHERE state = 'CE'
ORDER BY name;
```

### 3. Save a favorite query

After writing a query, click **Save Current Query** and give it a name.

### 4. Export to Excel

After running a `SELECT`, fill in the report name and click **Export Last Query Results**. The file will be saved in `relatorios_gerados/`.

<br>

## 🗺 Roadmap

| Feature | Status |
|---------|--------|
| Syntax highlighting in the SQL editor | 🔜 Planned |
| Results table with `QTableView` | 🔜 Planned |
| Async execution (threading) | 🔜 Planned |
| CSV and PDF export | 🔜 Planned |
| Query execution history | 🔜 Planned |
| Dark mode | 💡 Idea |
| Password encryption | 💡 Idea |

<br>

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request. To get started:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'feat: description of change'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

<br>

## 📄 License

This project is licensed under the [MIT License](LICENSE).

<br>

---

<div align="center">

Built with ☕ and 🐍 by **amonmelo**

<a href="https://www.linkedin.com/in/amonmelo/">![LinkedIn](https://img.shields.io/badge/LinkedIn-amonmelo-0A66C2?logo=linkedin&logoColor=white)</a>
<a href="https://github.com/amonmelo">![GitHub](https://img.shields.io/badge/GitHub-amonmelo-181717?logo=github&logoColor=white)</a>

</div>
