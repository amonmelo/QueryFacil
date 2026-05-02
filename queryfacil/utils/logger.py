"""Módulo de logging para QueryFacil."""

import os
import logging
from typing import Optional

from PyQt5.QtCore import QObject, pyqtSignal

from queryfacil.config import LOG_DIR, LOG_FILE, LOG_LEVEL


class QTextEditLogger(logging.Handler, QObject):
    """Handler de logging que envia mensagens para um signal PyQt5.

    Attributes:
        log_signal: Signal emitido com cada mensagem de log formatada.
    """

    log_signal = pyqtSignal(str)

    def __init__(self) -> None:
        """Inicializa o handler com formato padrão."""
        logging.Handler.__init__(self)
        QObject.__init__(self)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.setFormatter(formatter)

    def emit(self, record: logging.LogRecord) -> None:
        """Emite o record de log como signal.

        Args:
            record: Record de logging a ser formatado e emitido.
        """
        try:
            msg = self.format(record)
            self.log_signal.emit(msg)
        except Exception:
            self.handleError(record)


def setup_logging(log_file: Optional[str] = None) -> logging.Logger:
    """Configura o logging global da aplicação.

    Cria o diretório de logs se necessário e configura handlers
    de arquivo e console.

    Args:
        log_file: Caminho do arquivo de log. Se None, usa o padrão do config.

    Returns:
        Logger raiz configurado.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    target_file = log_file or LOG_FILE
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove handlers existentes para evitar duplicação
    root_logger.handlers.clear()

    # Handler de arquivo
    try:
        file_handler = logging.FileHandler(target_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        root_logger.addHandler(file_handler)
    except OSError as e:
        root_logger.warning(f"Não foi possível criar arquivo de log: {e}")

    # Handler de console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    )
    root_logger.addHandler(console_handler)

    root_logger.info("Logging inicializado.")
    return root_logger
