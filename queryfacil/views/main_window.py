"""Janela principal do QueryFacil.

Implementa a interface completa com:
- QSplitter para resizable panels
- QTableView para resultados (PandasModel)
- SQL Syntax Highlighter
- QStatusBar com info de conexão e tempo de execução
- Atalhos de teclado
- Threading com QThreadPool + QueryWorker
- Confirmação de queries destrutivas
"""

import logging
from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QPushButton, QTextEdit, QComboBox, QLineEdit,
    QLabel, QGroupBox, QMessageBox, QFileDialog, QDialog,
    QFormLayout, QDialogButtonBox, QCheckBox, QSizePolicy,
    QInputDialog, QStatusBar, QProgressBar, QTableView,
    QAction, QMenuBar,
)
from PyQt5.QtCore import Qt, QThreadPool, QSignalBlocker
from PyQt5.QtGui import QFont, QKeySequence

from queryfacil.config import (
    APP_NAME, DEFAULT_OUTPUT_DIR, MAX_ROWS_PREVIEW,
)
from queryfacil.services.db_manager import DBManager, SAVE_OK, SAVE_OVERWRITE_NEEDED
from queryfacil.services.postgres_service import PostgresService
from queryfacil.services.report_service import ReportService
from queryfacil.utils.logger import QTextEditLogger, setup_logging
from queryfacil.views.components.sql_highlighter import SQLHighlighter
from queryfacil.views.components.results_table import PandasModel, create_results_table
from queryfacil.views.dialogs.connection_dialog import (
    AddConnectionDialog, ManageConnectionsDialog,
)
from queryfacil.views.dialogs.query_dialog import ManageQueriesDialog
from queryfacil.workers.query_worker import QueryWorker

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Janela principal da aplicação QueryFacil.

    Gerencia a interface completa incluindo conexões, editor SQL,
    execução de queries, exibição de resultados e exportação.

    Attributes:
        db_manager: Gerenciador de banco de dados.
        postgres_service: Serviço de execução PostgreSQL.
        report_service: Serviço de geração de relatórios.
        thread_pool: Pool de threads para execução assíncrona.
    """

    def __init__(self) -> None:
        """Inicializa a janela principal e todos os componentes."""
        super().__init__()
        self.db_manager = DBManager()
        self.postgres_service = PostgresService()
        self.report_service = ReportService()
        self.thread_pool = QThreadPool.globalInstance()
        self.current_query: str = ""
        self.last_dataframe = None  # DataFrame completo dos últimos resultados
        self.is_executing: bool = False
        self.pending_destructive_query: Optional[str] = None

        self._init_ui()
        self._setup_shortcuts()
        self._setup_menu()
        self.load_connections()
        self.load_saved_queries_to_combobox()

    def _init_ui(self) -> None:
        """Inicializa todos os componentes da interface."""
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, 1100, 800)

        # Central widget com splitter
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # --- Connection Section ---
        self.conn_group = QGroupBox("Gerenciamento de Conexão")
        conn_layout = QHBoxLayout()

        self.conn_combo = QComboBox()
        self.conn_combo.setMinimumWidth(200)

        self.add_conn_button = QPushButton("Nova Conexão")
        self.add_conn_button.clicked.connect(self.show_add_connection_dialog)

        self.manage_conn_button = QPushButton("Gerenciar Conexões")
        self.manage_conn_button.clicked.connect(self.show_manage_connections_dialog)

        conn_layout.addWidget(QLabel("Conexão:"))
        conn_layout.addWidget(self.conn_combo)
        conn_layout.addWidget(self.add_conn_button)
        conn_layout.addWidget(self.manage_conn_button)
        conn_layout.addStretch(1)

        self.conn_group.setLayout(conn_layout)
        main_layout.addWidget(self.conn_group)

        # --- Query Section ---
        self.query_group = QGroupBox("Query SQL")
        query_layout = QVBoxLayout()

        query_manage_layout = QHBoxLayout()
        self.saved_query_combo = QComboBox()
        self.saved_query_combo.setMinimumWidth(200)

        self.save_query_button = QPushButton("Salvar Query")
        self.save_query_button.clicked.connect(self.save_current_query)

        self.manage_queries_button = QPushButton("Gerenciar Queries")
        self.manage_queries_button.clicked.connect(self.show_manage_queries_dialog)

        query_manage_layout.addWidget(QLabel("Query Salva:"))
        query_manage_layout.addWidget(self.saved_query_combo)
        query_manage_layout.addWidget(self.save_query_button)
        query_manage_layout.addWidget(self.manage_queries_button)
        query_manage_layout.addStretch(1)

        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText(
            "Digite sua query SQL aqui (ex: SELECT * FROM tabela;)"
        )
        self.query_input.setMinimumHeight(150)
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.query_input.setFont(font)
        self.query_input.textChanged.connect(self.update_current_query)

        # SQL Syntax Highlighter
        self.sql_highlighter = SQLHighlighter(self.query_input.document())

        # Execute button + progress
        exec_layout = QHBoxLayout()
        self.execute_button = QPushButton("Executar Query")
        self.execute_button.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold;"
        )
        self.execute_button.clicked.connect(self.execute_sql_query)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(0)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximumHeight(20)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid grey; border-radius: 3px; background: #f0f0f0; }"
            "QProgressBar::chunk { background: #4CAF50; width: 20px; margin: 1px; }"
        )

        exec_layout.addWidget(self.execute_button)
        exec_layout.addWidget(self.progress_bar)
        exec_layout.addStretch(1)

        query_layout.addLayout(query_manage_layout)
        query_layout.addWidget(self.query_input)
        query_layout.addLayout(exec_layout)
        self.query_group.setLayout(query_layout)
        main_layout.addWidget(self.query_group)

        # --- Results Section (QTableView) ---
        self.results_group = QGroupBox("Resultados")
        results_layout = QVBoxLayout()

        self.results_table = create_results_table()
        self.results_label = QLabel("Nenhum resultado para exibir.")
        self.results_label.setStyleSheet("color: gray; font-style: italic;")

        results_layout.addWidget(self.results_label)
        results_layout.addWidget(self.results_table)
        self.results_table.setVisible(False)
        self.results_group.setLayout(results_layout)
        main_layout.addWidget(self.results_group)

        # --- Output / Export Section ---
        self.output_group = QGroupBox("Exportar Resultados")
        output_layout = QVBoxLayout()

        output_format_layout = QHBoxLayout()
        self.excel_checkbox = QCheckBox("Excel (XLSX)")
        self.excel_checkbox.setChecked(True)
        output_format_layout.addWidget(self.excel_checkbox)
        output_format_layout.addStretch(1)

        output_dir_layout = QHBoxLayout()
        self.output_dir_label = QLabel(f"Diretório: {DEFAULT_OUTPUT_DIR}")
        self.change_dir_button = QPushButton("Alterar Diretório")
        self.change_dir_button.clicked.connect(self.change_output_directory)
        output_dir_layout.addWidget(self.output_dir_label)
        output_dir_layout.addWidget(self.change_dir_button)
        output_dir_layout.addStretch(1)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nome do Relatório:"))
        self.query_name_input = QLineEdit()
        self.query_name_input.setPlaceholderText("Nome do relatório (obrigatório para exportar)")
        name_layout.addWidget(self.query_name_input)

        self.export_button = QPushButton("Exportar Resultados")
        self.export_button.setStyleSheet(
            "background-color: #007BFF; color: white; font-weight: bold;"
        )
        self.export_button.clicked.connect(self.export_last_query_results)
        self.export_button.setEnabled(False)

        output_layout.addLayout(output_format_layout)
        output_layout.addLayout(output_dir_layout)
        output_layout.addLayout(name_layout)
        output_layout.addWidget(self.export_button)
        self.output_group.setLayout(output_layout)
        main_layout.addWidget(self.output_group)

        # --- Log Section ---
        self.log_group = QGroupBox("Logs")
        log_layout = QVBoxLayout()

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(100)
        self.log_output.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")

        log_layout.addWidget(self.log_output)
        self.log_group.setLayout(log_layout)
        main_layout.addWidget(self.log_group)

        # Logging para QTextEdit via signal
        self.log_handler = QTextEditLogger()
        self.log_handler.log_signal.connect(self.log_output.append)
        logging.getLogger().addHandler(self.log_handler)
        logging.info("Interface inicializada.")

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.connection_status_label = QLabel("Nenhuma conexão selecionada")
        self.execution_time_label = QLabel("")
        self.status_bar.addPermanentWidget(self.connection_status_label)
        self.status_bar.addPermanentWidget(self.execution_time_label)

        # Conecta sinais dos combos (após setup inicial)
        self.conn_combo.currentIndexChanged.connect(self.select_connection)
        self.saved_query_combo.currentIndexChanged.connect(self.select_saved_query)

    def _setup_menu(self) -> None:
        """Configura o menu bar da aplicação."""
        menubar = self.menuBar()

        # Menu Arquivo
        file_menu = menubar.addMenu("Arquivo")

        new_query_action = QAction("Nova Query", self)
        new_query_action.setShortcut("Ctrl+N")
        new_query_action.triggered.connect(self.new_query)
        file_menu.addAction(new_query_action)

        file_menu.addSeparator()

        exit_action = QAction("Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu Conexão
        conn_menu = menubar.addMenu("Conexão")

        add_conn_action = QAction("Nova Conexão", self)
        add_conn_action.setShortcut("Ctrl+Shift+C")
        add_conn_action.triggered.connect(self.show_add_connection_dialog)
        conn_menu.addAction(add_conn_action)

        manage_conn_action = QAction("Gerenciar Conexões", self)
        manage_conn_action.setShortcut("Ctrl+Shift+M")
        manage_conn_action.triggered.connect(self.show_manage_connections_dialog)
        conn_menu.addAction(manage_conn_action)

        # Menu Query
        query_menu = menubar.addMenu("Query")

        save_query_action = QAction("Salvar Query", self)
        save_query_action.setShortcut("Ctrl+S")
        save_query_action.triggered.connect(self.save_current_query)
        query_menu.addAction(save_query_action)

        exec_query_action = QAction("Executar Query", self)
        exec_query_action.setShortcut("Ctrl+Enter")
        exec_query_action.triggered.connect(self.execute_sql_query)
        query_menu.addAction(exec_query_action)

        manage_query_action = QAction("Gerenciar Queries", self)
        manage_query_action.setShortcut("Ctrl+Shift+Q")
        manage_query_action.triggered.connect(self.show_manage_queries_dialog)
        query_menu.addAction(manage_query_action)

        # Menu Exportação
        export_menu = menubar.addMenu("Exportar")

        export_action = QAction("Exportar Resultados", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_last_query_results)
        export_menu.addAction(export_action)

    def _setup_shortcuts(self) -> None:
        """Configura atalhos de teclado adicionais se necessário.

        A maioria dos atalhos é configurada via menu actions.
        """
        pass  # Atalhos configurados em _setup_menu

    # --- Connection Methods ---

    def load_connections(self) -> None:
        """Carrega a lista de conexões no combobox.

        Preserva a seleção atual se possível.
        """
        current_text = self.conn_combo.currentText() if self.conn_combo.count() > 0 else ""

        with QSignalBlocker(self.conn_combo):
            self.conn_combo.clear()
            self.conn_combo.addItem("Selecione uma conexão...")

            connections = self.db_manager.get_connections()
            connection_names = [conn["name"] for conn in connections]

            for name in connection_names:
                self.conn_combo.addItem(name)

            # Restaura seleção
            if current_text in connection_names and current_text != "Selecione uma conexão...":
                self.conn_combo.setCurrentText(current_text)
            else:
                self.conn_combo.setCurrentIndex(0)

        # Dispara seleção manualmente
        self.select_connection()
        logger.info(f"{len(connections)} conexões carregadas.")

    def show_add_connection_dialog(self) -> None:
        """Abre o diálogo para adicionar nova conexão."""
        dialog = AddConnectionDialog(self.db_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_connection_data()
            success, error = self.db_manager.add_connection(**data)
            if success:
                QMessageBox.information(self, "Sucesso", "Conexão adicionada com sucesso!")
                self.load_connections()
            else:
                QMessageBox.warning(self, "Erro", f"Não foi possível adicionar: {error}")

    def show_manage_connections_dialog(self) -> None:
        """Abre o diálogo de gerenciamento de conexões."""
        dialog = ManageConnectionsDialog(self.db_manager, self)
        dialog.connectionChanged.connect(self.load_connections)
        dialog.exec_()

    def select_connection(self) -> None:
        """Seleciona a conexão atual do combobox."""
        selected_name = self.conn_combo.currentText()
        if selected_name == "Selecione uma conexão...":
            self.db_manager.current_db_config = None
            self.postgres_service.set_connection_config(None)
            self.connection_status_label.setText("Nenhuma conexão selecionada")
            self.last_dataframe = None
            self.export_button.setEnabled(False)
            self._clear_results()
            logger.info("Nenhuma conexão selecionada.")
            return

        config = self.db_manager.get_connection_by_name(selected_name)
        if config:
            self.postgres_service.set_connection_config(config)
            self.connection_status_label.setText(f"Conectado a: {selected_name}")
            self.last_dataframe = None
            self.export_button.setEnabled(False)
            logger.info(f"Conexão '{selected_name}' selecionada.")
        else:
            QMessageBox.critical(
                self, "Erro",
                "Configuração não encontrada. Selecione outra ou adicione uma nova."
            )
            logger.error(f"Configuração para '{selected_name}' não encontrada.")
            self.last_dataframe = None
            self.export_button.setEnabled(False)

    # --- Saved Queries Methods ---

    def load_saved_queries_to_combobox(self) -> None:
        """Carrega a lista de queries salvas no combobox."""
        with QSignalBlocker(self.saved_query_combo):
            self.saved_query_combo.clear()
            self.saved_query_combo.addItem("Selecione uma query...")

            queries = self.db_manager.get_saved_queries()
            for name, _ in queries:
                self.saved_query_combo.addItem(name)

        logger.info(f"{len(queries)} queries salvas carregadas.")

    def select_saved_query(self) -> None:
        """Carrega a query selecionada no editor."""
        selected_name = self.saved_query_combo.currentText()
        if selected_name == "Selecione uma query...":
            logger.info("Nenhuma query salva selecionada.")
            return

        query_text = self.db_manager.get_query_by_name(selected_name)
        if query_text:
            with QSignalBlocker(self.query_input):
                self.query_input.setPlainText(query_text)
            self.current_query = query_text
            logger.info(f"Query salva carregada: '{selected_name}'")
        else:
            QMessageBox.warning(self, "Erro", f"Query '{selected_name}' não encontrada.")
            with QSignalBlocker(self.saved_query_combo):
                self.saved_query_combo.setCurrentIndex(0)

    def update_current_query(self) -> None:
        """Atualiza self.current_query e reseta o combo de queries salvas."""
        new_text = self.query_input.toPlainText()
        if new_text != self.current_query:
            self.current_query = new_text
            with QSignalBlocker(self.saved_query_combo):
                self.saved_query_combo.setCurrentIndex(0)

    def save_current_query(self) -> None:
        """Salva a query atual do editor."""
        query_text = self.query_input.toPlainText().strip()
        if not query_text:
            QMessageBox.warning(self, "Atenção", "O editor está vazio.")
            return

        query_name, ok = QInputDialog.getText(self, "Salvar Query", "Nome da query:")
        if ok and query_name:
            query_name = query_name.strip()
            if not query_name:
                QMessageBox.warning(self, "Nome Inválido", "O nome não pode estar vazio.")
                return

            status, data = self.db_manager.save_query(query_name, query_text)

            if status == SAVE_OK:
                QMessageBox.information(self, "Sucesso", f"Query '{query_name}' salva!")
                self.load_saved_queries_to_combobox()
                with QSignalBlocker(self.saved_query_combo):
                    self.saved_query_combo.setCurrentText(query_name)
            elif status == SAVE_OVERWRITE_NEEDED:
                reply = QMessageBox.question(
                    self, "Query Existe",
                    f"Já existe uma query com o nome '{query_name}'. Sobrescrever?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
                )
                if reply == QMessageBox.Yes:
                    status2, _ = self.db_manager.save_query(query_name, query_text, overwrite=True)
                    if status2 == SAVE_OK:
                        QMessageBox.information(self, "Sucesso", f"Query '{query_name}' atualizada!")
                        self.load_saved_queries_to_combobox()
                        with QSignalBlocker(self.saved_query_combo):
                            self.saved_query_combo.setCurrentText(query_name)
            else:
                QMessageBox.warning(self, "Erro", f"Erro ao salvar: {data}")
        elif ok:
            QMessageBox.warning(self, "Nome Inválido", "O nome não pode estar vazio.")

    def show_manage_queries_dialog(self) -> None:
        """Abre o diálogo de gerenciamento de queries salvas."""
        dialog = ManageQueriesDialog(self.db_manager, self)
        dialog.queryChanged.connect(self.load_saved_queries_to_combobox)
        dialog.queryLoaded.connect(self._on_query_loaded_from_dialog)
        dialog.exec_()

    def _on_query_loaded_from_dialog(self, query_name: str, query_text: str) -> None:
        """Callback quando uma query é carregada do diálogo de gerenciamento.

        Args:
            query_name: Nome da query.
            query_text: Texto SQL da query.
        """
        with QSignalBlocker(self.query_input):
            self.query_input.setPlainText(query_text)
        self.current_query = query_text
        self.load_saved_queries_to_combobox()
        with QSignalBlocker(self.saved_query_combo):
            self.saved_query_combo.setCurrentText(query_name)

    # --- Query Execution ---

    def execute_sql_query(self) -> None:
        """Inicia a execução da query SQL em thread separada."""
        if self.is_executing:
            self.status_bar.showMessage("Execução em andamento...", 3000)
            return

        if not self.db_manager.current_db_config:
            QMessageBox.warning(self, "Atenção", "Selecione uma conexão antes de executar.")
            return

        query = self.query_input.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Atenção", "Digite uma query SQL.")
            return

        self._set_executing_state(True)

        worker = QueryWorker(query, self.postgres_service)
        worker.signals.started.connect(self._on_query_started)
        worker.signals.finished.connect(self._on_query_finished)
        worker.signals.destructive_confirmation.connect(self._on_destructive_confirmation)

        self.thread_pool.start(worker)

    def _on_query_started(self) -> None:
        """Callback quando a execução da query começa."""
        logger.info("Execução de query iniciada...")
        self.status_bar.showMessage("Executando query...", 0)

    def _on_query_finished(
        self, success: bool, data: object, error: str, row_count: int, elapsed_ms: float
    ) -> None:
        """Callback quando a execução da query termina.

        Args:
            success: Se a execução foi bem-sucedida.
            data: DataFrame (SELECT) ou string de mensagem (DML).
            error: Mensagem de erro, se houver.
            row_count: Número de linhas retornadas.
            elapsed_ms: Tempo de execução em milissegundos.
        """
        self._set_executing_state(False)
        self.status_bar.clearMessage()

        if not success:
            if error and "destrutiva não confirmada" not in error.lower():
                QMessageBox.critical(self, "Erro na Query", error)
                logger.error(f"Query falhou: {error}")
            return

        # DML/DDL com sucesso
        if data is None:
            msg = error or "Comando SQL executado com sucesso."
            self.status_bar.showMessage(f"Comando executado em {elapsed_ms:.0f}ms", 5000)
            self.execution_time_label.setText(f"Executado em {elapsed_ms:.0f}ms")
            self.log_output.append(f"\n--- {msg} ---")
            self._clear_results()
            self.export_button.setEnabled(False)
            QMessageBox.information(self, "Sucesso", msg)
            return

        # SELECT com resultados
        import pandas as pd
        df: pd.DataFrame = data
        self.last_dataframe = df

        total_rows = len(df)
        preview_rows = min(total_rows, MAX_ROWS_PREVIEW)
        df_preview = df.head(preview_rows) if total_rows > MAX_ROWS_PREVIEW else df

        # Atualiza QTableView
        model = PandasModel(df_preview)
        self.results_table.setModel(model)
        self.results_table.setVisible(True)
        self.results_label.setVisible(False)

        if total_rows > MAX_ROWS_PREVIEW:
            self.results_label.setText(
                f"Mostrando {preview_rows} de {total_rows} linhas."
            )
            self.results_label.setVisible(True)
        elif total_rows == 0:
            self.results_label.setText("Nenhum resultado retornado.")
            self.results_label.setVisible(True)
            self.results_table.setVisible(False)
        else:
            self.results_label.setText(f"{total_rows} linhas retornadas.")
            self.results_label.setVisible(True)

        # Atualiza status bar
        self.execution_time_label.setText(
            f"Query executada em {elapsed_ms:.0f}ms — {total_rows} linhas"
        )
        self.status_bar.showMessage(
            f"Query executada em {elapsed_ms:.0f}ms — {row_count} linhas", 10000
        )

        # Log
        self.log_output.append(
            f"\n--- Query executada com sucesso: {total_rows} linhas em {elapsed_ms:.0f}ms ---"
        )
        if not df.empty:
            preview_text = df.to_string(index=False, max_rows=20, max_colwidth=30, line_width=100)
            self.log_output.append(preview_text)
            if total_rows > 20:
                self.log_output.append(f"... ({total_rows - 20} mais linhas. Exporte para ver todas.)")

        self.export_button.setEnabled(True)

    def _on_destructive_confirmation(self, query_text: str) -> None:
        """Pede confirmação ao usuário para query destrutiva.

        Args:
            query_text: Texto da query que precisa confirmação.
        """
        self._set_executing_state(False)
        self.status_bar.clearMessage()

        reply = QMessageBox.warning(
            self, "Query Destrutiva",
            "Esta query pode modificar ou destruir dados permanentemente:\n\n"
            f"{query_text[:200]}{'...' if len(query_text) > 200 else ''}\n\n"
            "Deseja executar mesmo assim?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Re-executa com confirmação
            self._set_executing_state(True)
            worker = QueryWorker(query_text, self.postgres_service, skip_confirmation=True)
            worker.signals.finished.connect(self._on_query_finished)
            self.thread_pool.start(worker)

    def _set_executing_state(self, executing: bool) -> None:
        """Atualiza o estado visual de execução.

        Args:
            executing: Se está executando ou não.
        """
        self.is_executing = executing
        self.execute_button.setEnabled(not executing)
        self.progress_bar.setVisible(executing)

    def _clear_results(self) -> None:
        """Limpa a tabela de resultados."""
        self.results_table.setModel(None)
        self.results_table.setVisible(False)
        self.results_label.setText("Nenhum resultado para exibir.")
        self.results_label.setVisible(True)

    # --- Export ---

    def export_last_query_results(self) -> None:
        """Exporta os últimos resultados para Excel."""
        if self.last_dataframe is None:
            QMessageBox.warning(self, "Atenção", "Nenhum resultado para exportar.")
            return

        query_name = self.query_name_input.text().strip()
        if not query_name:
            QMessageBox.warning(self, "Atenção", "Informe o nome do relatório.")
            return

        selected_db_name = self.conn_combo.currentText()

        generated_files: list = []
        if self.excel_checkbox.isChecked():
            path = self.report_service.generate_excel(
                self.last_dataframe, query_name, selected_db_name
            )
            if path:
                generated_files.append(f"Excel: {path}")

        if generated_files:
            self.log_output.append("\nRelatórios gerados:")
            for f in generated_files:
                self.log_output.append(f"  {f}")
            self.status_bar.showMessage("Relatório exportado com sucesso!", 5000)
            QMessageBox.information(self, "Sucesso", "Relatório gerado com sucesso!")
        else:
            QMessageBox.warning(
                self, "Nenhum Formato",
                "Marque 'Excel (XLSX)' para gerar o relatório."
            )

    def change_output_directory(self) -> None:
        """Abre diálogo para alterar diretório de saída."""
        new_dir = QFileDialog.getExistingDirectory(
            self, "Selecionar Diretório de Saída", DEFAULT_OUTPUT_DIR
        )
        if new_dir:
            self.report_service.output_dir = new_dir
            self.output_dir_label.setText(f"Diretório: {new_dir}")
            logger.info(f"Diretório de saída alterado: {new_dir}")
            QMessageBox.information(
                self, "Diretório Alterado",
                f"O diretório de saída foi alterado para:\n{new_dir}"
            )

    # --- Utility Methods ---

    def new_query(self) -> None:
        """Limpa o editor de query."""
        self.query_input.clear()
        self.current_query = ""
        with QSignalBlocker(self.saved_query_combo):
            self.saved_query_combo.setCurrentIndex(0)
        logger.info("Editor limpo.")

    def closeEvent(self, event) -> None:
        """Trata o evento de fechamento da janela.

        Args:
            event: Evento de fechamento.
        """
        self.db_manager.close()
        logger.info("Aplicação encerrada.")
        super().closeEvent(event)
