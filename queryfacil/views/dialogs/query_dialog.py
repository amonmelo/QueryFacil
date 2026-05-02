"""Diálogo de gerenciamento de queries salvas.

Desacoplado via signal queryChanged().
"""

import logging
from typing import Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QWidget,
)
from PyQt5.QtCore import Qt, pyqtSignal

from queryfacil.services.db_manager import DBManager

logger = logging.getLogger(__name__)


class ManageQueriesDialog(QDialog):
    """Diálogo para gerenciar queries salvas.

    Emite queryChanged() e queryLoaded(query_name, query_text) quando
    uma query é carregada para o editor.

    Signals:
        queryChanged: Emitido quando a lista de queries muda (add/delete).
        queryLoaded: Emitido quando uma query é carregada (nome, texto).
    """

    queryChanged = pyqtSignal()
    queryLoaded = pyqtSignal(str, str)

    def __init__(
        self,
        db_manager: DBManager,
        parent: Optional[QWidget] = None,
    ) -> None:
        """Inicializa o diálogo.

        Args:
            db_manager: Instância do DBManager.
            parent: Widget pai.
        """
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Gerenciar Queries Salvas")
        self.setGeometry(250, 250, 500, 350)

        self._build_ui()
        self._load_query_list()

    def _build_ui(self) -> None:
        """Constrói a interface do diálogo."""
        self.main_layout = QVBoxLayout()

        self.query_list_widget = QListWidget()
        self.query_list_widget.itemSelectionChanged.connect(self._update_button_states)
        self.main_layout.addWidget(self.query_list_widget)

        self.button_layout = QHBoxLayout()
        self.load_button = QPushButton("Carregar Query")
        self.load_button.clicked.connect(self._load_selected_query)
        self.load_button.setEnabled(False)

        self.delete_button = QPushButton("Excluir Query")
        self.delete_button.clicked.connect(self._delete_selected_query)
        self.delete_button.setEnabled(False)

        self.button_layout.addWidget(self.load_button)
        self.button_layout.addWidget(self.delete_button)
        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)

    def _load_query_list(self) -> None:
        """Carrega a lista de queries salvas."""
        self.query_list_widget.clear()
        queries = self.db_manager.get_saved_queries()
        for name, query_text in queries:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, query_text)
            self.query_list_widget.addItem(item)
        self._update_button_states()

    def _update_button_states(self) -> None:
        """Habilita/desabilita botões baseado na seleção."""
        has_selection = len(self.query_list_widget.selectedItems()) > 0
        self.load_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _load_selected_query(self) -> None:
        """Carrega a query selecionada para o editor via signal."""
        selected_items = self.query_list_widget.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        query_text = item.data(Qt.UserRole)
        query_name = item.text()

        self.queryLoaded.emit(query_name, query_text)
        QMessageBox.information(self, "Query Carregada", f"Query '{query_name}' carregada no editor.")
        self.accept()

    def _delete_selected_query(self) -> None:
        """Exclui a query selecionada após confirmação."""
        selected_items = self.query_list_widget.selectedItems()
        if not selected_items:
            return

        query_name = selected_items[0].text()

        reply = QMessageBox.question(
            self, "Confirmar Exclusão",
            f"Deseja realmente excluir a query '{query_name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            success, msg = self.db_manager.delete_query(query_name)
            if success:
                QMessageBox.information(self, "Sucesso", f"Query '{query_name}' excluída.")
                self._load_query_list()
                self.queryChanged.emit()
            else:
                QMessageBox.warning(self, "Erro", f"Não foi possível excluir: {msg}")
