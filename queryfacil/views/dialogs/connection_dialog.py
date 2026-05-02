"""Diálogos de gerenciamento de conexões.

AddConnectionDialog e ManageConnectionsDialog, desacoplados via signals.
"""

import logging
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QDialogButtonBox,
    QMessageBox, QComboBox, QListWidget, QListWidgetItem,
    QWidget,
)
from PyQt5.QtCore import Qt, pyqtSignal

from queryfacil.services.db_manager import DBManager
from queryfacil.config import APP_NAME

logger = logging.getLogger(__name__)


class AddConnectionDialog(QDialog):
    """Diálogo para adicionar ou editar uma conexão PostgreSQL.

    Attributes:
        db_manager: Instância do DBManager.
        connection_data: Dados da conexão em edição (None para nova).
        old_name: Nome anterior da conexão (para updates).
    """

    def __init__(
        self,
        db_manager: DBManager,
        parent: Optional[QWidget] = None,
        connection_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Inicializa o diálogo.

        Args:
            db_manager: Instância do DBManager.
            parent: Widget pai.
            connection_data: Dados para modo de edição.
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.connection_data = connection_data
        self.old_name = connection_data["name"] if connection_data else None

        self.setWindowTitle(
            f"Editar Conexão: {connection_data['name']}" if connection_data else "Nova Conexão"
        )
        self.setFixedSize(400, 380)

        self._build_ui()

        # Popula campos se em modo edição
        if self.connection_data:
            self.name_input.setText(self.connection_data["name"])
            self.host_input.setText(self.connection_data["host"])
            self.port_input.setText(str(self.connection_data["port"]))
            self.dbname_input.setText(self.connection_data["dbname"])
            self.user_input.setText(self.connection_data["user"])
            # Mostra senha descriptografada
            from queryfacil.utils.crypto import decrypt_password
            pwd = self.connection_data.get("password", "")
            if isinstance(pwd, bytes):
                pwd = decrypt_password(pwd)
            self.password_input.setText(pwd)

    def _build_ui(self) -> None:
        """Constrói a interface do diálogo."""
        self.form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome da conexão")
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("localhost")
        self.port_input = QLineEdit("5432")
        self.dbname_input = QLineEdit()
        self.dbname_input.setPlaceholderText("nome_do_banco")
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("usuario")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("senha")

        self.test_conn_button = QPushButton("Testar Conexão")
        self.test_conn_button.clicked.connect(self._test_connection)
        self.test_result_label = QLabel("")
        self.test_result_label.setStyleSheet("color: red;")

        self.form_layout.addRow("Nome:", self.name_input)
        self.form_layout.addRow("Host:", self.host_input)
        self.form_layout.addRow("Porta:", self.port_input)
        self.form_layout.addRow("Banco de Dados:", self.dbname_input)
        self.form_layout.addRow("Usuário:", self.user_input)
        self.form_layout.addRow("Senha:", self.password_input)
        self.form_layout.addRow(self.test_conn_button)
        self.form_layout.addRow(self.test_result_label)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self._validate_and_accept)
        self.button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.form_layout)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def _test_connection(self) -> None:
        """Testa a conexão com os dados atuais do formulário."""
        port_str = self.port_input.text().strip()
        try:
            port = int(port_str)
        except ValueError:
            self.test_result_label.setText(
                "<font color='red'>Porta inválida. Use um número inteiro.</font>"
            )
            return

        success, error = self.db_manager.test_connection(
            self.host_input.text(),
            port,
            self.dbname_input.text(),
            self.user_input.text(),
            self.password_input.text(),
        )
        if success:
            self.test_result_label.setText("<font color='green'>Conexão bem-sucedida!</font>")
        else:
            self.test_result_label.setText(f"<font color='red'>Falha: {error}</font>")

    def _validate_and_accept(self) -> None:
        """Valida os dados e aceita o diálogo se tudo estiver OK."""
        name = self.name_input.text().strip()
        host = self.host_input.text().strip()
        port_str = self.port_input.text().strip()
        dbname = self.dbname_input.text().strip()
        user = self.user_input.text().strip()
        password = self.password_input.text()

        if not all([name, host, port_str, dbname, user]):
            QMessageBox.warning(self, "Campos Obrigatórios", "Preencha todos os campos.")
            return

        try:
            port = int(port_str)
        except ValueError:
            QMessageBox.warning(self, "Porta Inválida", "A porta deve ser um número inteiro.")
            return

        if port < 1 or port > 65535:
            QMessageBox.warning(self, "Porta Inválida", "A porta deve estar entre 1 e 65535.")
            return

        # Testa conexão antes de aceitar
        success, error = self.db_manager.test_connection(host, port, dbname, user, password)
        if not success:
            QMessageBox.warning(
                self, "Conexão Falhou",
                f"Não foi possível conectar com os dados fornecidos:\n{error}"
            )
            return

        self.accept()

    def get_connection_data(self) -> Dict[str, Any]:
        """Retorna os dados do formulário como dicionário.

        Returns:
            Dicionário com name, host, port, dbname, user, password.
        """
        port_str = self.port_input.text().strip()
        try:
            port = int(port_str)
        except ValueError:
            port = 5432

        return {
            "name": self.name_input.text().strip(),
            "host": self.host_input.text().strip(),
            "port": port,
            "dbname": self.dbname_input.text().strip(),
            "user": self.user_input.text().strip(),
            "password": self.password_input.text(),
        }


class ManageConnectionsDialog(QDialog):
    """Diálogo para gerenciar conexões cadastradas.

    Emite connectionChanged() quando uma conexão é adicionada,
    editada ou removida, para desacoplamento da MainWindow.

    Signals:
        connectionChanged: Emitido quando a lista de conexões muda.
    """

    connectionChanged = pyqtSignal()

    def __init__(
        self,
        db_manager: DBManager,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Inicializa o diálogo de gerenciamento.

        Args:
            db_manager: Instância do DBManager.
            parent: Widget pai.
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Gerenciar Conexões")
        self.setGeometry(200, 200, 600, 400)

        self._build_ui()
        self._load_connections_list()

    def _build_ui(self) -> None:
        """Constrói a interface do diálogo."""
        self.main_layout = QVBoxLayout()

        self.conn_list_widget = QListWidget()
        self.conn_list_widget.itemSelectionChanged.connect(self._update_button_states)
        self.main_layout.addWidget(self.conn_list_widget)

        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Nova Conexão")
        self.add_button.clicked.connect(self._add_connection)
        self.edit_button = QPushButton("Editar Conexão")
        self.edit_button.clicked.connect(self._edit_connection)
        self.edit_button.setEnabled(False)
        self.delete_button = QPushButton("Remover Conexão")
        self.delete_button.clicked.connect(self._delete_connection)
        self.delete_button.setEnabled(False)

        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.edit_button)
        self.button_layout.addWidget(self.delete_button)
        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)

    def _load_connections_list(self) -> None:
        """Carrega a lista de conexões no widget."""
        self.conn_list_widget.clear()
        connections = self.db_manager.get_connections()
        for conn_data in connections:
            item = QListWidgetItem(conn_data["name"])
            item.setData(Qt.UserRole, conn_data)
            self.conn_list_widget.addItem(item)
        self._update_button_states()

    def _update_button_states(self) -> None:
        """Habilita/desabilita botões baseado na seleção."""
        has_selection = len(self.conn_list_widget.selectedItems()) > 0
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _add_connection(self) -> None:
        """Abre o diálogo para adicionar nova conexão."""
        dialog = AddConnectionDialog(self.db_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_connection_data()
            success, error = self.db_manager.add_connection(**data)
            if success:
                QMessageBox.information(self, "Sucesso", "Conexão adicionada com sucesso!")
                self._load_connections_list()
                self.connectionChanged.emit()
            else:
                QMessageBox.warning(self, "Erro", f"Não foi possível adicionar: {error}")

    def _edit_connection(self) -> None:
        """Abre o diálogo para editar conexão selecionada."""
        selected_items = self.conn_list_widget.selectedItems()
        if not selected_items:
            return

        conn_data = selected_items[0].data(Qt.UserRole)

        dialog = AddConnectionDialog(self.db_manager, self, connection_data=conn_data)
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_connection_data()
            old_name = conn_data["name"]
            success, msg = self.db_manager.update_connection(old_name, **new_data)
            if success:
                QMessageBox.information(
                    self, "Sucesso",
                    f"Conexão '{old_name}' atualizada para '{new_data['name']}'!"
                )
                self._load_connections_list()
                self.connectionChanged.emit()
            else:
                QMessageBox.warning(self, "Erro", f"Não foi possível atualizar: {msg}")

    def _delete_connection(self) -> None:
        """Remove a conexão selecionada após confirmação."""
        selected_items = self.conn_list_widget.selectedItems()
        if not selected_items:
            return

        conn_data = selected_items[0].data(Qt.UserRole)
        conn_name = conn_data["name"]

        reply = QMessageBox.question(
            self, "Confirmar Remoção",
            f"Deseja realmente remover a conexão '{conn_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            success, msg = self.db_manager.delete_connection(conn_name)
            if success:
                QMessageBox.information(self, "Sucesso", f"Conexão '{conn_name}' removida!")
                self._load_connections_list()
                self.connectionChanged.emit()
            else:
                QMessageBox.warning(self, "Erro", f"Não foi possível remover: {msg}")
