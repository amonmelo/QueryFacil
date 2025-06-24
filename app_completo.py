# app_completo.py

import os
import sqlite3
import pandas as pd
import psycopg2
import logging
from datetime import datetime

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QTextEdit, QComboBox, QLineEdit, QLabel, QGroupBox,
    QMessageBox, QFileDialog, QDialog, QFormLayout, QDialogButtonBox,
    QCheckBox, QSizePolicy, QListWidget, QListWidgetItem, QInputDialog
)
from PyQt5.QtCore import Qt


# --- 1. Configurações Globais ---
APP_NAME = "Gerador de Relatórios SQL"
SQLITE_DB_PATH = "db_connections.db" # This DB will now also store queries
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")
DEFAULT_OUTPUT_DIR = "relatorios_gerados"

# Ensure log and output directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

# Basic logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(LOG_FILE),
                        logging.StreamHandler()
                    ])

# --- 2. Database Connection and Query Management ---
class DBManager:
    def __init__(self):
        self.conn_sqlite = None
        self._init_sqlite_db()
        self.current_db_config = None # Stores the currently selected database configuration
        self.last_query_df = None # Stores the last DataFrame from a SELECT query

    def _init_sqlite_db(self):
        try:
            self.conn_sqlite = sqlite3.connect(SQLITE_DB_PATH)
            cursor = self.conn_sqlite.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS connections (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    host TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    dbname TEXT NOT NULL,
                    user TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS saved_queries (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    query_text TEXT NOT NULL
                )
            ''')
            self.conn_sqlite.commit()
            logging.info("SQLite database initialized/verified successfully.")
        except sqlite3.Error as e:
            logging.error(f"Error initializing SQLite database: {e}")

    def test_connection(self, host, port, dbname, user, password):
        conn = None
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=dbname,
                user=user,
                password=password,
                options='-c client_encoding=LATIN1',
                connect_timeout=5 # Adds a timeout for the connection
            )
            logging.info(f"Connection test successful for {user}@{host}:{port}/{dbname}")
            return True, None
        except psycopg2.Error as e:
            logging.error(f"Connection test failed: {e}")
            return False, str(e)
        finally:
            if conn:
                conn.close()

    def add_connection(self, name, host, port, dbname, user, password):
        # Test connection before adding
        success, error_msg = self.test_connection(host, port, dbname, user, password)
        if not success:
            logging.warning(f"Could not add connection '{name}' due to failed connection test: {error_msg}")
            return False, f"Connection test failed: {error_msg}"

        try:
            cursor = self.conn_sqlite.cursor()
            cursor.execute('''
                INSERT INTO connections (name, host, port, dbname, user, password)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, host, port, dbname, user, password))
            self.conn_sqlite.commit()
            logging.info(f"Connection '{name}' added successfully.")
            return True, None
        except sqlite3.IntegrityError:
            logging.warning(f"Error: A connection with the name '{name}' already exists.")
            return False, f"A connection with the name '{name}' already exists."
        except sqlite3.Error as e:
            logging.error(f"Error adding connection: {e}")
            return False, f"Error adding connection: {e}"

    def update_connection(self, old_name, name, host, port, dbname, user, password):
        # Test connection before updating
        success, error_msg = self.test_connection(host, port, dbname, user, password)
        if not success:
            logging.warning(f"Could not update connection '{name}' due to failed connection test: {error_msg}")
            return False, f"Connection test failed: {error_msg}"

        try:
            cursor = self.conn_sqlite.cursor()
            # If the name changed, check for uniqueness
            if old_name != name:
                cursor.execute("SELECT id FROM connections WHERE name = ?", (name,))
                if cursor.fetchone():
                    logging.warning(f"Error: A connection with the name '{name}' already exists.")
                    return False, f"A connection with the new name '{name}' already exists."
            
            cursor.execute('''
                UPDATE connections
                SET name = ?, host = ?, port = ?, dbname = ?, user = ?, password = ?
                WHERE name = ?
            ''', (name, host, port, dbname, user, password, old_name))
            self.conn_sqlite.commit()
            logging.info(f"Connection '{old_name}' updated to '{name}' successfully.")
            return True, None
        except sqlite3.Error as e:
            logging.error(f"Error updating connection: {e}")
            return False, f"Error updating connection: {e}"

    def delete_connection(self, name):
        try:
            cursor = self.conn_sqlite.cursor()
            cursor.execute("DELETE FROM connections WHERE name = ?", (name,))
            self.conn_sqlite.commit()
            logging.info(f"Connection '{name}' removed successfully.")
            return True, None
        except sqlite3.Error as e:
            logging.error(f"Error removing connection: {e}")
            return False, f"Error removing connection: {e}"

    def get_connections(self):
        try:
            cursor = self.conn_sqlite.cursor()
            cursor.execute("SELECT id, name, host, port, dbname, user, password FROM connections")
            return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting connections: {e}")
            return []

    def get_connection_by_name(self, name):
        try:
            cursor = self.conn_sqlite.cursor()
            cursor.execute("SELECT host, port, dbname, user, password FROM connections WHERE name = ?", (name,))
            result = cursor.fetchone()
            if result:
                self.current_db_config = {
                    'host': result[0], 'port': result[1], 'dbname': result[2],
                    'user': result[3], 'password': result[4]
                }
                return self.current_db_config
            return None
        except sqlite3.Error as e:
            logging.error(f"Error getting connection by name: {e}")
            return None

    # --- Saved Query Management ---
    def save_query(self, name, query_text):
        try:
            cursor = self.conn_sqlite.cursor()
            # Check if query name already exists
            cursor.execute("SELECT id FROM saved_queries WHERE name = ?", (name,))
            if cursor.fetchone():
                reply = QMessageBox.question(None, 'Query Exists', 
                                             f"A query with the name '{name}' already exists. Do you want to overwrite it?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.No:
                    return False, "Save cancelled by user."
                cursor.execute("UPDATE saved_queries SET query_text = ? WHERE name = ?", (query_text, name))
                self.conn_sqlite.commit()
                logging.info(f"Query '{name}' updated successfully.")
                return True, None
            else:
                cursor.execute("INSERT INTO saved_queries (name, query_text) VALUES (?, ?)", (name, query_text))
                self.conn_sqlite.commit()
                logging.info(f"Query '{name}' saved successfully.")
                return True, None
        except sqlite3.Error as e:
            logging.error(f"Error saving query: {e}")
            return False, f"Error saving query: {e}"

    def get_saved_queries(self):
        try:
            cursor = self.conn_sqlite.cursor()
            cursor.execute("SELECT name, query_text FROM saved_queries ORDER BY name")
            return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Error getting saved queries: {e}")
            return []

    def get_query_by_name(self, name):
        try:
            cursor = self.conn_sqlite.cursor()
            cursor.execute("SELECT query_text FROM saved_queries WHERE name = ?", (name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            logging.error(f"Error retrieving saved query: {e}")
            return None

    def delete_query(self, name):
        try:
            cursor = self.conn_sqlite.cursor()
            cursor.execute("DELETE FROM saved_queries WHERE name = ?", (name,))
            self.conn_sqlite.commit()
            logging.info(f"Query '{name}' deleted successfully.")
            return True, None
        except sqlite3.Error as e:
            logging.error(f"Error deleting query: {e}")
            return False, f"Error deleting query: {e}"

    def execute_query(self, query):
        self.last_query_df = None # Reset the DataFrame of the last query
        if not self.current_db_config:
            logging.warning("No database connection selected.")
            return None, "No database connection selected."

        conn = None
        try:
            conn = psycopg2.connect(
                host=self.current_db_config['host'],
                port=self.current_db_config['port'],
                database=self.current_db_config['dbname'],
                user=self.current_db_config['user'],
                password=self.current_db_config['password'],
                options='-c client_encoding=LATIN1' # Ensures LATIN1 encoding
            )
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Try to fetch results if the query is a SELECT
            try:
                columns = [desc[0] for desc in cursor.description]
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=columns)
                self.last_query_df = df # Store the DataFrame
                logging.info("SELECT query executed successfully.")
                return df, None
            except psycopg2.ProgrammingError: # No results to fetch (e.g., INSERT, UPDATE, DELETE)
                conn.commit() # Commit for DML queries
                logging.info("SQL command (DML) executed successfully.")
                return None, "SQL command executed successfully (no data returned)."

        except psycopg2.Error as e:
            logging.error(f"Error executing query: {e}")
            return None, f"Error executing query: {e}"
        finally:
            if conn:
                conn.close()

    def close(self):
        if self.conn_sqlite:
            self.conn_sqlite.close()
            logging.info("SQLite connection closed.")

# --- 3. Report Generation ---
class ReportGenerator:
    def __init__(self, output_dir=DEFAULT_OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_output_path(self, base_name, extension, db_name):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sub_dir = os.path.join(self.output_dir, f"{db_name}_{timestamp}")
        os.makedirs(sub_dir, exist_ok=True)
        return os.path.join(sub_dir, f"{base_name}_{timestamp}.{extension}")

    # generate_pdf and generate_txt methods are removed

    def generate_excel(self, dataframe, query_name, db_name):
        file_path = self._get_output_path(query_name, "xlsx", db_name)
        try:
            writer = pd.ExcelWriter(file_path, engine='openpyxl')
            dataframe.to_excel(writer, index=False, sheet_name='Dados')
            
            # Auto-adjust columns in Excel
            workbook = writer.book
            worksheet = writer.sheets['Dados']
            for column in worksheet.columns:
                max_length = 0
                column_name = column[0].value # Get column name
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except TypeError:
                        pass # Ignore empty or non-text cells
                adjusted_width = (max_length + 2) * 1.2 # Adjustment factor
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
            
            writer.close()
            logging.info(f"Excel '{file_path}' generated successfully.")
            return file_path
        except Exception as e:
            logging.error(f"Error generating Excel: {e}")
            return None

# --- 4. PyQt5 User Interface ---
class AddConnectionDialog(QDialog):
    def __init__(self, db_manager, parent=None, connection_data=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.connection_data = connection_data # For edit mode
        self.old_name = connection_data['name'] if connection_data else None

        if connection_data:
            self.setWindowTitle(f"Edit Connection: {connection_data['name']}")
        else:
            self.setWindowTitle("Add New Connection")
        
        self.setFixedSize(400, 350) 

        self.form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.host_input = QLineEdit()
        self.port_input = QLineEdit("5432")
        self.dbname_input = QLineEdit()
        self.user_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.test_conn_button = QPushButton("Test Connection")
        self.test_conn_button.clicked.connect(self.test_connection_in_dialog)
        self.test_result_label = QLabel("")
        self.test_result_label.setStyleSheet("color: red;")

        self.form_layout.addRow("Connection Name:", self.name_input)
        self.form_layout.addRow("Host:", self.host_input)
        self.form_layout.addRow("Port:", self.port_input)
        self.form_layout.addRow("Database Name:", self.dbname_input)
        self.form_layout.addRow("User:", self.user_input)
        self.form_layout.addRow("Password:", self.password_input)
        self.form_layout.addRow(self.test_conn_button)
        self.form_layout.addRow(self.test_result_label)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept_and_save) 
        self.button_box.rejected.connect(self.reject)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addWidget(self.button_box)
        self.setLayout(self.main_layout)

        # Populate fields if in edit mode
        if self.connection_data:
            self.name_input.setText(self.connection_data['name'])
            self.host_input.setText(self.connection_data['host'])
            self.port_input.setText(str(self.connection_data['port']))
            self.dbname_input.setText(self.connection_data['dbname'])
            self.user_input.setText(self.connection_data['user'])
            self.password_input.setText(self.connection_data['password']) # Populates existing password

    def test_connection_in_dialog(self):
        host = self.host_input.text()
        port = int(self.port_input.text())
        dbname = self.dbname_input.text()
        user = self.user_input.text()
        password = self.password_input.text()

        success, error_msg = self.db_manager.test_connection(host, port, dbname, user, password)
        if success:
            self.test_result_label.setText("<font color='green'>Connection successful!</font>")
        else:
            self.test_result_label.setText(f"<font color='red'>Connection failed: {error_msg}</font>")

    def accept_and_save(self):
        host = self.host_input.text()
        port = int(self.port_input.text())
        dbname = self.dbname_input.text()
        user = self.user_input.text()
        password = self.password_input.text()

        success, error_msg = self.db_manager.test_connection(host, port, dbname, user, password)
        if not success:
            QMessageBox.warning(self, "Connection Failed", f"Could not connect to the database with the provided data:\n{error_msg}")
            return # Don't close the window if connection fails

        # If the test is successful, then accept the dialog
        self.accept()

    def get_connection_data(self):
        return {
            "name": self.name_input.text(),
            "host": self.host_input.text(),
            "port": int(self.port_input.text()),
            "dbname": self.dbname_input.text(),
            "user": self.user_input.text(),
            "password": self.password_input.text()
        }

class ManageConnectionsDialog(QDialog):
    def __init__(self, db_manager, main_window_ref, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.main_window_ref = main_window_ref # Reference to the main window to reload connections
        self.setWindowTitle("Manage Connections")
        self.setGeometry(200, 200, 600, 400)

        self.main_layout = QVBoxLayout()

        self.conn_list_widget = QListWidget()
        self.conn_list_widget.itemSelectionChanged.connect(self._update_button_states)
        self.main_layout.addWidget(self.conn_list_widget)

        self.button_layout = QHBoxLayout()
        self.edit_button = QPushButton("Edit Connection")
        self.edit_button.clicked.connect(self._edit_connection)
        self.edit_button.setEnabled(False) # Disabled by default

        self.delete_button = QPushButton("Remove Connection")
        self.delete_button.clicked.connect(self._delete_connection)
        self.delete_button.setEnabled(False) # Disabled by default

        self.button_layout.addWidget(self.edit_button)
        self.button_layout.addWidget(self.delete_button)
        self.main_layout.addLayout(self.button_layout)
        
        self.setLayout(self.main_layout)
        self._load_connections_list()

    def _load_connections_list(self):
        self.conn_list_widget.clear()
        connections = self.db_manager.get_connections()
        for conn_id, name, host, port, dbname, user, password in connections:
            item = QListWidgetItem(name)
            # Store all connection data in the item for easy access
            item.setData(Qt.UserRole, {
                'id': conn_id, 'name': name, 'host': host, 'port': port,
                'dbname': dbname, 'user': user, 'password': password
            })
            self.conn_list_widget.addItem(item)
        self._update_button_states()

    def _update_button_states(self):
        has_selection = len(self.conn_list_widget.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _edit_connection(self):
        selected_items = self.conn_list_widget.selectedItems()
        if not selected_items:
            return

        selected_item = selected_items[0]
        conn_data = selected_item.data(Qt.UserRole)

        dialog = AddConnectionDialog(self.db_manager, self, connection_data=conn_data)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_connection_data()
            old_name = conn_data['name']
            success, msg = self.db_manager.update_connection(old_name, **new_data)
            if success:
                QMessageBox.information(self, "Success", f"Connection '{old_name}' updated to '{new_data['name']}'!")
                self._load_connections_list() # Reload the dialog list
                self.main_window_ref.load_connections() # Reload the main window combobox
            else:
                QMessageBox.warning(self, "Error", f"Could not update connection: {msg}")

    def _delete_connection(self):
        selected_items = self.conn_list_widget.selectedItems()
        if not selected_items:
            return

        selected_item = selected_items[0]
        conn_data = selected_item.data(Qt.UserRole)
        conn_name = conn_data['name']

        reply = QMessageBox.question(self, 'Confirm Deletion', 
                                     f"Are you sure you want to remove connection '{conn_name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            success, msg = self.db_manager.delete_connection(conn_name)
            if success:
                QMessageBox.information(self, "Success", f"Connection '{conn_name}' removed successfully!")
                self._load_connections_list() # Reload the dialog list
                self.main_window_ref.load_connections() # Reload the main window combobox
            else:
                QMessageBox.warning(self, "Error", f"Could not remove connection: {msg}")

# --- Saved Query Management Dialog ---
class ManageQueriesDialog(QDialog):
    def __init__(self, db_manager, main_window_ref, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.main_window_ref = main_window_ref # Reference to main window to update query text
        self.setWindowTitle("Manage Saved Queries")
        self.setGeometry(250, 250, 500, 350)

        self.main_layout = QVBoxLayout()

        self.query_list_widget = QListWidget()
        self.query_list_widget.itemSelectionChanged.connect(self._update_button_states)
        self.main_layout.addWidget(self.query_list_widget)

        self.button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load Query")
        self.load_button.clicked.connect(self._load_selected_query)
        self.load_button.setEnabled(False)

        self.delete_button = QPushButton("Delete Query")
        self.delete_button.clicked.connect(self._delete_selected_query)
        self.delete_button.setEnabled(False)

        self.button_layout.addWidget(self.load_button)
        self.button_layout.addWidget(self.delete_button)
        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)
        self._load_query_list()

    def _load_query_list(self):
        self.query_list_widget.clear()
        queries = self.db_manager.get_saved_queries()
        for name, query_text in queries:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, query_text) # Store the query text in the item
            self.query_list_widget.addItem(item)
        self._update_button_states()
        self.main_window_ref.load_saved_queries_to_combobox() # Update main window combobox

    def _update_button_states(self):
        has_selection = len(self.query_list_widget.selectedItems()) > 0
        self.load_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _load_selected_query(self):
        selected_items = self.query_list_widget.selectedItems()
        if not selected_items:
            return
        
        selected_item = selected_items[0]
        query_text = selected_item.data(Qt.UserRole)
        query_name = selected_item.text()
        
        self.main_window_ref.query_input.setPlainText(query_text)
        # Set the combobox to the loaded query, but ensure select_saved_query is handled carefully
        self.main_window_ref.load_saved_queries_to_combobox() # Reload all queries
        self.main_window_ref.saved_query_combo.setCurrentText(query_name) # Set to loaded query
        
        QMessageBox.information(self, "Query Loaded", f"Query '{query_name}' loaded to editor.")
        self.accept() # Close dialog after loading

    def _delete_selected_query(self):
        selected_items = self.query_list_widget.selectedItems()
        if not selected_items:
            return

        selected_item = selected_items[0]
        query_name = selected_item.text()

        reply = QMessageBox.question(self, 'Confirm Deletion', 
                                     f"Are you sure you want to delete query '{query_name}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success, msg = self.db_manager.delete_query(query_name)
            if success:
                QMessageBox.information(self, "Success", f"Query '{query_name}' deleted.")
                self._load_query_list() # Reload list in this dialog
                self.main_window_ref.load_saved_queries_to_combobox() # Reload combobox in main window
            else:
                QMessageBox.warning(self, "Error", f"Could not delete query: {msg}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DBManager()
        self.report_generator = ReportGenerator()
        self.init_ui()
        self.load_connections() # Load connections on startup
        self.load_saved_queries_to_combobox() # Load saved queries on startup
        self.current_query = "" # This will hold the query text currently in the QTextEdit
        self.last_dataframe_for_export = None # To store the DataFrame for later export

    def init_ui(self):
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, 1000, 700) # Initial window size

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # --- Connection Section ---
        self.conn_group = QGroupBox("Connection Management")
        self.conn_layout = QHBoxLayout()

        self.conn_combo = QComboBox()
        self.conn_combo.setMinimumWidth(200)
        # Connect AFTER initial load for manual control
        
        self.add_conn_button = QPushButton("Add Connection")
        self.add_conn_button.clicked.connect(self.show_add_connection_dialog)

        self.manage_conn_button = QPushButton("Manage Connections")
        self.manage_conn_button.clicked.connect(self.show_manage_connections_dialog)

        self.conn_layout.addWidget(QLabel("Connection:"))
        self.conn_layout.addWidget(self.conn_combo)
        self.conn_layout.addWidget(self.add_conn_button)
        self.conn_layout.addWidget(self.manage_conn_button) 
        self.conn_layout.addStretch(1) 

        self.conn_group.setLayout(self.conn_layout)
        self.main_layout.addWidget(self.conn_group)

        # --- SQL Query Section ---
        self.query_group = QGroupBox("SQL Query")
        self.query_layout = QVBoxLayout()

        # Query Management row
        self.query_manage_layout = QHBoxLayout()
        self.saved_query_combo = QComboBox()
        self.saved_query_combo.setMinimumWidth(200)
        # Connect this after loading queries.
        
        self.save_query_button = QPushButton("Save Current Query")
        self.save_query_button.clicked.connect(self.save_current_query)

        self.manage_queries_button = QPushButton("Manage Saved Queries")
        self.manage_queries_button.clicked.connect(self.show_manage_queries_dialog)

        self.query_manage_layout.addWidget(QLabel("Saved Query:"))
        self.query_manage_layout.addWidget(self.saved_query_combo)
        self.query_manage_layout.addWidget(self.save_query_button)
        self.query_manage_layout.addWidget(self.manage_queries_button)
        self.query_manage_layout.addStretch(1)

        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText("Enter your SQL query here (e.g., SELECT * FROM your_table;)")
        self.query_input.setMinimumHeight(150)
        self.query_input.textChanged.connect(self.update_current_query) # This will also reset saved_query_combo

        self.execute_button = QPushButton("Execute Query")
        self.execute_button.clicked.connect(self.execute_sql_query)
        self.execute_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")

        self.query_layout.addLayout(self.query_manage_layout) # Add query management row
        self.query_layout.addWidget(self.query_input)
        self.query_layout.addWidget(self.execute_button)
        self.query_group.setLayout(self.query_layout)
        self.main_layout.addWidget(self.query_group)

        # --- Output Options Section ---
        self.output_group = QGroupBox("Report Output Options")
        self.output_layout = QVBoxLayout()

        self.format_layout = QHBoxLayout()
        # Removed PDF and TXT checkboxes
        self.excel_checkbox = QCheckBox("Excel (XLSX)")
        self.excel_checkbox.setChecked(True) # Default to Excel
        self.format_layout.addWidget(self.excel_checkbox)
        self.format_layout.addStretch(1)

        self.output_dir_layout = QHBoxLayout()
        self.output_dir_label = QLabel(f"Output Directory: {DEFAULT_OUTPUT_DIR}")
        self.change_dir_button = QPushButton("Change Directory")
        self.change_dir_button.clicked.connect(self.change_output_directory)
        self.output_dir_layout.addWidget(self.output_dir_label)
        self.output_dir_layout.addWidget(self.change_dir_button)
        self.output_dir_layout.addStretch(1)

        self.query_name_input = QLineEdit()
        self.query_name_input.setPlaceholderText("Report Name (required for export)") # Now required as only one format
        
        self.export_button = QPushButton("Export Last Query Results")
        self.export_button.clicked.connect(self.export_last_query_results)
        self.export_button.setEnabled(False) # Disabled until a DF is available for export
        self.export_button.setStyleSheet("background-color: #007BFF; color: white; font-weight: bold;")


        self.output_layout.addLayout(self.format_layout)
        self.output_layout.addLayout(self.output_dir_layout)
        self.output_layout.addWidget(QLabel("Report Name:"))
        self.output_layout.addWidget(self.query_name_input)
        self.output_layout.addWidget(self.export_button)
        
        self.output_group.setLayout(self.output_layout)
        self.main_layout.addWidget(self.output_group)

        # --- Logs and Output Section ---
        self.log_group = QGroupBox("Logs and Query Output")
        self.log_layout = QVBoxLayout()

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(150)
        self.log_output.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")

        self.log_layout.addWidget(self.log_output)
        self.log_group.setLayout(self.log_layout)
        self.main_layout.addWidget(self.log_group)
        
        # Redirect Python logs to QTextEdit
        self.log_handler = QTextEditLogger(self.log_output)
        logging.getLogger().addHandler(self.log_handler)
        logging.info("Interface initialized.")

        # Set resizing policy
        self.central_widget.setSizePolicy(
            self.central_widget.sizePolicy().horizontalPolicy(),
            self.central_widget.sizePolicy().verticalPolicy()
        )
        self.query_input.setSizePolicy(
            self.query_input.sizePolicy().horizontalPolicy(),
            QSizePolicy.Expanding
        )
        self.log_output.setSizePolicy(
            self.log_output.sizePolicy().horizontalPolicy(),
            QSizePolicy.Expanding
        )
        self.main_layout.setStretch(1, 2) # Gives more space to the query input
        self.main_layout.setStretch(3, 1) # Gives space to the log output
        
        # Connect the currentIndexChanged signal AFTER initial setup, to allow manual control
        self.conn_combo.currentIndexChanged.connect(self.select_connection)
        self.saved_query_combo.currentIndexChanged.connect(self.select_saved_query)


    def update_current_query(self):
        # Update self.current_query and reset saved_query_combo if text changes
        new_text = self.query_input.toPlainText()
        if new_text != self.current_query:
            self.current_query = new_text
            # Disconnect to prevent infinite loop or unwanted triggers
            try:
                self.saved_query_combo.currentIndexChanged.disconnect(self.select_saved_query)
            except TypeError:
                pass
            self.saved_query_combo.setCurrentIndex(0) # Set to "Select query..."
            self.saved_query_combo.currentIndexChanged.connect(self.select_saved_query)


    def load_connections(self):
        # Store the currently selected connection, if any, to try and restore it later
        current_selected_text = self.conn_combo.currentText() if self.conn_combo.count() > 0 else ""
        
        # Disconnect signal temporarily to prevent unwanted triggers during population
        try:
            self.conn_combo.currentIndexChanged.disconnect(self.select_connection)
        except TypeError: 
            pass

        self.conn_combo.clear()
        self.conn_combo.addItem("Select a connection...") # Always the first item
        
        connections = self.db_manager.get_connections()
        connection_names = [conn[1] for conn in connections] # List only connection names
        
        for name in connection_names:
            self.conn_combo.addItem(name)
        
        # Restore previous selection if it still exists AND is not the default "Select a connection..."
        if current_selected_text in connection_names and current_selected_text != "Select a connection...":
            self.conn_combo.setCurrentText(current_selected_text)
            self.select_connection() # Manually trigger selection logic for restoration
        else:
            self.conn_combo.setCurrentIndex(0) # Default to "Select a connection..." (index 0)
            self.select_connection() # Manually trigger this state to clear current_db_config

        # Reconnect the signal
        self.conn_combo.currentIndexChanged.connect(self.select_connection)
        
        logging.info(f"{len(connections)} connections loaded.")


    def show_add_connection_dialog(self):
        dialog = AddConnectionDialog(self.db_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_connection_data()
            success, error_msg = self.db_manager.add_connection(**data)
            if success:
                QMessageBox.information(self, "Success", "Connection added and tested successfully!")
                self.load_connections() # Reload the combo box
            else:
                QMessageBox.warning(self, "Error", f"Could not add connection: {error_msg}")

    def show_manage_connections_dialog(self):
        dialog = ManageConnectionsDialog(self.db_manager, self, self) 
        dialog.exec_()
        self.load_connections() # Ensure combobox is reloaded after management

    def select_connection(self):
        selected_name = self.conn_combo.currentText()
        if selected_name == "Select a connection...":
            self.db_manager.current_db_config = None
            logging.info("No database connection selected.")
            self.last_dataframe_for_export = None
            self.export_button.setEnabled(False)
            self.log_output.clear() 
            self.log_output.append("Select a connection to continue or add a new one.")
            return

        config = self.db_manager.get_connection_by_name(selected_name)
        if config:
            logging.info(f"Connection '{selected_name}' selected.")
            self.log_output.clear() 
            self.log_output.append(f"Connected to: {selected_name}")
            self.last_dataframe_for_export = None
            self.export_button.setEnabled(False)
        else:
            QMessageBox.critical(self, "Error", "Connection configuration not found. Please select another or add a new one.")
            logging.error(f"Configuration for '{selected_name}' not found.")
            self.last_dataframe_for_export = None
            self.export_button.setEnabled(False)

    # --- Saved Queries Methods ---
    def load_saved_queries_to_combobox(self):
        # Disconnect signal temporarily
        try:
            self.saved_query_combo.currentIndexChanged.disconnect(self.select_saved_query)
        except TypeError:
            pass

        self.saved_query_combo.clear()
        self.saved_query_combo.addItem("Select a query...")
        queries = self.db_manager.get_saved_queries()
        for name, _ in queries:
            self.saved_query_combo.addItem(name)
        
        # Reconnect signal
        self.saved_query_combo.currentIndexChanged.connect(self.select_saved_query)
        logging.info(f"{len(queries)} saved queries loaded.")

    def select_saved_query(self):
        selected_name = self.saved_query_combo.currentText()
        if selected_name == "Select a query...":
            # Do not clear current_query, as user might be editing or manually typing
            logging.info("No saved query selected.")
            return

        query_text = self.db_manager.get_query_by_name(selected_name)
        if query_text:
            # Disconnect to avoid triggering update_current_query and resetting the combo again
            try:
                self.query_input.textChanged.disconnect(self.update_current_query)
            except TypeError:
                pass
            
            self.query_input.setPlainText(query_text)
            self.current_query = query_text # Ensure current_query is up-to-date
            logging.info(f"Loaded saved query: '{selected_name}'")
            
            # Reconnect
            self.query_input.textChanged.connect(self.update_current_query)
        else:
            QMessageBox.warning(self, "Error", f"Saved query '{selected_name}' not found.")
            logging.error(f"Saved query '{selected_name}' not found.")
            self.saved_query_combo.setCurrentIndex(0) # Reset to "Select a query..."


    def save_current_query(self):
        query_text = self.query_input.toPlainText().strip()
        if not query_text:
            QMessageBox.warning(self, "Attention", "The query editor is empty. Please enter a query to save.")
            return

        query_name, ok = QInputDialog.getText(self, "Save Query", "Enter a name for this query:")
        if ok and query_name:
            query_name = query_name.strip()
            if not query_name:
                QMessageBox.warning(self, "Invalid Name", "Query name cannot be empty.")
                return

            success, msg = self.db_manager.save_query(query_name, query_text)
            if success:
                QMessageBox.information(self, "Success", f"Query '{query_name}' saved successfully!")
                self.load_saved_queries_to_combobox()
                self.saved_query_combo.setCurrentText(query_name) # Select the newly saved query
            else:
                QMessageBox.warning(self, "Error Saving Query", msg)
        elif ok: # If OK clicked but name is empty
            QMessageBox.warning(self, "Invalid Name", "Query name cannot be empty.")

    def show_manage_queries_dialog(self):
        dialog = ManageQueriesDialog(self.db_manager, self, self)
        dialog.exec_()
        self.load_saved_queries_to_combobox() # Reload combobox after management

    # --- End Saved Queries Methods ---

    def execute_sql_query(self):
        if not self.db_manager.current_db_config:
            QMessageBox.warning(self, "Attention", "Please select a database connection first.")
            return

        query = self.query_input.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Attention", "Please enter an SQL query.")
            return

        selected_db_name = self.conn_combo.currentText()

        self.log_output.append(f"\n--- Executing query for '{selected_db_name}' ---")
        df, error = self.db_manager.execute_query(query)
        self.last_dataframe_for_export = df # Store the DF for later use

        if error:
            QMessageBox.critical(self, "Query Error", error)
            self.log_output.append(f"Error: {error}")
            self.export_button.setEnabled(False)
            return
        
        if df is None: # DML command (INSERT, UPDATE, DELETE)
            self.log_output.append("SQL command executed successfully (no results to export).")
            QMessageBox.information(self, "Success", "SQL command executed successfully!")
            self.export_button.setEnabled(False) # Disable export for DML
            return
        
        # If it reached here, it's a SELECT with results
        self.log_output.append("\nQuery executed successfully. Results:")
        
        # Display the first 20 rows and all columns in the log for readability
        if not df.empty:
            self.log_output.append(df.to_string(index=False, max_rows=20, max_colwidth=30, line_width=100))
            if len(df) > 20:
                self.log_output.append(f"... ({len(df) - 20} more rows. Export to see all.)")
        else:
            self.log_output.append("No data returned for the query.")

        self.export_button.setEnabled(True) # Enable the export button
        QMessageBox.information(self, "Query Executed", "SQL query executed successfully! You can now export the results.")
        
        # Keep the query on screen
        self.query_input.setPlainText(self.current_query) # Ensure the text in the editor remains, not cleared.

    def export_last_query_results(self):
        if self.last_dataframe_for_export is None:
            QMessageBox.warning(self, "Attention", "No query results to export. Execute a SELECT query first.")
            return

        query_name = self.query_name_input.text().strip()
        if not query_name:
            QMessageBox.warning(self, "Attention", "Please enter a name for the report before exporting.")
            return

        selected_db_name = self.conn_combo.currentText()
        
        generated_files = []
        # Only Excel generation remains
        if self.excel_checkbox.isChecked():
            path = self.report_generator.generate_excel(self.last_dataframe_for_export, query_name, selected_db_name)
            if path: generated_files.append(f"Excel: {path}")
        
        if generated_files:
            self.log_output.append("\nReport files generated:")
            for f in generated_files:
                self.log_output.append(f)
            QMessageBox.information(self, "Reports Generated", "Reports generated successfully!")
        else:
            QMessageBox.warning(self, "No Format Selected", "Please ensure 'Excel (XLSX)' is checked for generation.")

    def change_output_directory(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory", DEFAULT_OUTPUT_DIR)
        if new_dir:
            self.report_generator.output_dir = new_dir
            self.output_dir_label.setText(f"Output Directory: {new_dir}")
            logging.info(f"Output directory changed to: {new_dir}")
            QMessageBox.information(self, "Directory Changed", f"The output directory has been changed to:\n{new_dir}")

    def closeEvent(self, event):
        self.db_manager.close()
        logging.info("Application closed.")
        super().closeEvent(event)

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = parent
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.setFormatter(formatter)

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)
        sb = self.widget.verticalScrollBar()
        sb.setValue(sb.maximum())

# --- Application Execution ---
if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()