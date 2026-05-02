"""Entry point principal do QueryFacil (python main.py)."""

import sys
from PyQt5.QtWidgets import QApplication
from queryfacil.config import APP_NAME
from queryfacil.utils.logger import setup_logging
from queryfacil.views.main_window import MainWindow


def main() -> None:
    """Inicializa e executa a aplicação QueryFacil."""
    setup_logging()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
