<div align="center">

🇧🇷 [Português](README.md) | 🇺🇸 [English](README.en.md) | 🇪🇸 [Español](README.es.md) | 🇩🇪 [Deutsch](README.de.md)

</div>

<br>

<div align="center">

# ⚡ QueryFacil

**Herramienta de escritorio para optimizar y gestionar consultas SQL con una interfaz gráfica intuitiva.**

Conéctate a PostgreSQL, ejecuta queries, guarda tus favoritas y exporta los resultados a Excel — todo en un solo lugar.

![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-41CD52?logo=qt&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Connected-336791?logo=postgresql&logoColor=white)
![License MIT](https://img.shields.io/badge/License-MIT-green.svg)

![Desktop App](https://img.shields.io/badge/Type-Desktop_Application-informational)
![Cross Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-orange)
![SQLite Local](https://img.shields.io/badge/Storage-Local_SQLite-critical)

</div>

<br>

## 📸 Interfaz

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Generador de Reportes SQL                                   ─  □  X   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─── Gestión de Conexiones ──────────────────────────────────────────┐  │
│  │ Conexión:  [▼ Producción DB     ] [Agregar Conexión] [Gestionar]  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─── Consulta SQL ──────────────────────────────────────────────────┐  │
│  │ Query Guardada: [▼ Clientes por UF ] [Guardar Actual] [Gestionar]│  │
│  │ ┌────────────────────────────────────────────────────────────────┐ │  │
│  │ │ SELECT nombre, ciudad, estado                                 │ │  │
│  │ │ FROM tab_clientes                                             │ │  │
│  │ │ WHERE estado = 'CE'                                           │ │  │
│  │ │ ORDER BY nombre;                                              │ │  │
│  │ └────────────────────────────────────────────────────────────────┘ │  │
│  │                              [ ▶  Ejecutar Query                 ]  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─── Opciones de Exportación ──────────────────────────────────────┐  │
│  │ [✓] Excel (XLSX)    Salida: relatorios_gerados/                  │  │
│  │ Nombre Reporte: [ clientes_ceara ]  [ 📥 Exportar Últimos       ] │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─── Logs y Resultados ────────────────────────────────────────────┐  │
│  │ 2026-01-15 10:32 - INFO - Conectado a: Producción DB            │  │
│  │ 2026-01-15 10:32 - INFO - SELECT ejecutada exitosamente.        │  │
│  │       nombre          ciudad        estado                       │  │
│  │  ─────────────────────────────────────────────────               │  │
│  │  Ana Silva         Fortaleza       CE                           │  │
│  │  Carlos Souza      Sobral         CE                            │  │
│  │  ... (148 filas más. Exporta para ver todas.)                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

<br>

## ✅ Funcionalidades

| Recurso | Detalles |
|---------|----------|
| ✅ **Múltiples conexiones** | Agrega, edita y gestiona varias conexiones PostgreSQL |
| ✅ **Prueba de conexión** | Valida la conexión antes de guardar |
| ✅ **Editor SQL integrado** | Escribe y ejecuta queries directamente en la interfaz |
| ✅ **Queries favoritas** | Guarda, carga y gestiona tus queries más usadas |
| ✅ **Exportación Excel** | Genera reportes `.xlsx` con columnas auto-ajustadas |
| ✅ **Soporte LATIN1** | Compatible con bases en codificación LATIN1/UTF-8 |
| ✅ **Logs en tiempo real** | Visualiza los logs dentro de la aplicación |
| ✅ **Almacenamiento local** | Todo guardado en SQLite — sin depender de la nube |
| ✅ **Multi-plataforma** | Funciona en Windows, Linux y macOS |

<br>

## 🛠 Stack Técnica

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI_5.15%2B-41CD52?logo=qt&logoColor=white)
![psycopg2](https://img.shields.io/badge/psycopg2-binary-PostgreSQL_Driver-336791?logo=postgresql&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-Manipulación_Datos-150458?logo=pandas&logoColor=white)
![openpyxl](https://img.shields.io/badge/openpyxl-Generación_Excel-217346?logo=openxml&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Almacenamiento_Local-003B57?logo=sqlite&logoColor=white)

<br>

## 🏗 Arquitectura

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
│           │  (Core)   │  ← sqlite3 → Config Local   │
│           └─────┬─────┘                             │
│                 ▼                                   │
│     ┌────────────────────┐                          │
│     │ ReportGenerator    │  → pandas + openpyxl     │
│     └────────────────────┘     → .xlsx files        │
└─────────────────────────────────────────────────────┘
```

<br>

## 📦 Instalación

### Requisitos previos

- Python 3.8 o superior
- PostgreSQL accesible (local o remoto)

### Paso a paso

```bash
# 1. Clona el repositorio
git clone https://github.com/amonmelo/QueryFacil.git
cd QueryFacil

# 2. (Opcional) Crea un entorno virtual
python -m venv venv

# Activa el entorno
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Ejecuta la aplicación
python app_completo.py
```

<br>

## 🚀 Cómo Usar

### 1. Agregar una conexión

Haz clic en **Agregar Conexión**, completa los datos del banco y prueba la conexión:

```
Host: 192.168.1.100
Port: 5432
Database: mi_base
User: postgres
Password: ********
```

### 2. Ejecutar una query

Selecciona la conexión en el combo, escribe tu SQL y haz clic en **Ejecutar Query**:

```sql
SELECT nombre, ciudad, estado
FROM tab_clientes
WHERE estado = 'CE'
ORDER BY nombre;
```

### 3. Guardar query favorita

Después de escribir una query, haz clic en **Guardar Query Actual** y ponle un nombre.

### 4. Exportar a Excel

Después de ejecutar un `SELECT`, completa el nombre del reporte y haz clic en **Exportar Últimos Resultados**. El archivo se guardará en `relatorios_gerados/`.

<br>

## 🗺 Roadmap

| Recurso | Estado |
|---------|--------|
| Syntax highlighting en el editor SQL | 🔜 Planeado |
| Tabla de resultados con `QTableView` | 🔜 Planeado |
| Ejecución asíncrona (threading) | 🔜 Planeado |
| Exportación a CSV y PDF | 🔜 Planeado |
| Historial de queries ejecutadas | 🔜 Planeado |
| Modo oscuro | 💡 Idea |
| Cifrado de contraseñas | 💡 Idea |

<br>

## 🤝 Contribuyendo

¡Las contribuciones son bienvenidas! No dudes en abrir un issue o enviar un pull request. Para empezar:

1. Haz un fork del proyecto
2. Crea una branch con tu feature (`git checkout -b feature/mi-feature`)
3. Haz commit de tus cambios (`git commit -m 'feat: descripción del cambio'`)
4. Push a la branch (`git push origin feature/mi-feature`)
5. Abre un Pull Request

<br>

## 📄 Licencia

Este proyecto está licenciado bajo la [Licencia MIT](LICENSE).

<br>

---

<div align="center">

Hecho con ☕ y 🐍 por **amonmelo**

<a href="https://www.linkedin.com/in/amonmelo/">![LinkedIn](https://img.shields.io/badge/LinkedIn-amonmelo-0A66C2?logo=linkedin&logoColor=white)</a>
<a href="https://github.com/amonmelo">![GitHub](https://img.shields.io/badge/GitHub-amonmelo-181717?logo=github&logoColor=white)</a>

</div>
