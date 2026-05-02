"""Configurações globais do QueryFacil."""

import os

APP_NAME = "QueryFacil"
APP_VERSION = "2.0.0"
SQLITE_DB_PATH = "db_connections.db"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
DEFAULT_OUTPUT_DIR = "relatorios_gerados"
MAX_ROWS_PREVIEW = 1000
DEFAULT_QUERY_TIMEOUT = 30  # seconds
DEFAULT_CONNECT_TIMEOUT = 5  # seconds
DEFAULT_ENCODING = "LATIN1"
LOG_LEVEL = "INFO"
