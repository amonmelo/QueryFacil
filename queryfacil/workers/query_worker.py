"""Worker para execução assíncrona de queries SQL.

Usa QRunnable com signals para não bloquear a thread principal da GUI.
"""

import time
import logging
from typing import Optional

from PyQt5.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot

from queryfacil.services.postgres_service import PostgresService

logger = logging.getLogger(__name__)


class QueryWorkerSignals(QObject):
    """Signals emitidos pelo QueryWorker durante a execução.

    Signals:
        started: Emitido quando a execução começa.
        finished: Emitido quando a execução termina.
            Args: success (bool), data (DataFrame ou str), error (str),
                  row_count (int), elapsed_ms (float).
        destructive_confirmation: Emitido quando a query é destrutiva.
            Args: query_text (str) — a query que precisa confirmação.
    """

    started = pyqtSignal()
    finished = pyqtSignal(bool, object, str, int, float)
    destructive_confirmation = pyqtSignal(str)


class QueryWorker(QRunnable):
    """Worker para executar queries SQL em thread separada.

    Attributes:
        query: Texto SQL da query.
        postgres_service: Instância do PostgresService configurada.
        skip_confirmation: Se True, executa sem pedir confirmação destrutiva.
        signals: Instância de QueryWorkerSignals.
    """

    def __init__(
        self,
        query: str,
        postgres_service: PostgresService,
        skip_confirmation: bool = False,
    ) -> None:
        """Inicializa o worker.

        Args:
            query: Texto SQL da query.
            postgres_service: Serviço PostgreSQL configurado.
            skip_confirmation: Se True, pula verificação de query destrutiva.
        """
        super().__init__()
        self.query = query
        self.postgres_service = postgres_service
        self.skip_confirmation = skip_confirmation
        self.signals = QueryWorkerSignals()
        self.setAutoDelete(True)

    @pyqtSlot()
    def run(self) -> None:
        """Executa a query em background e emite signals de resultado."""
        self.signals.started.emit()

        # Verificação de query destrutiva
        if not self.skip_confirmation and self.postgres_service.is_destructive_query(self.query):
            self.signals.destructive_confirmation.emit(self.query)
            # Termina sem executar — a MainWindow vai re-disparar se confirmado
            self.signals.finished.emit(
                False, None, "Execução cancelada: query destrutiva não confirmada.", 0, 0.0
            )
            return

        start_time = time.time()
        try:
            df_or_none, error = self.postgres_service.execute_query(self.query)
            elapsed_ms = (time.time() - start_time) * 1000

            if error and df_or_none is None:
                # Erro real
                self.signals.finished.emit(False, None, error, 0, elapsed_ms)
            elif df_or_none is not None:
                # SELECT com resultados
                row_count = len(df_or_none)
                self.signals.finished.emit(True, df_or_none, "", row_count, elapsed_ms)
            else:
                # DML/DDL com sucesso
                self.signals.finished.emit(True, None, error or "", 0, elapsed_ms)

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            msg = f"Erro inesperado: {e}"
            logger.exception(msg)
            self.signals.finished.emit(False, None, msg, 0, elapsed_ms)
