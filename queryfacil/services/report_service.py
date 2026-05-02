"""Serviço de geração de relatórios Excel."""

import os
import re
import logging
from typing import Optional
from datetime import datetime

import pandas as pd

from queryfacil.config import DEFAULT_OUTPUT_DIR

logger = logging.getLogger(__name__)


class ReportService:
    """Serviço para gerar relatórios em Excel.

    Attributes:
        output_dir: Diretório de saída dos relatórios.
    """

    def __init__(self, output_dir: str = DEFAULT_OUTPUT_DIR) -> None:
        """Inicializa o serviço de relatórios.

        Args:
            output_dir: Caminho do diretório de saída.
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def sanitize_filename(self, name: str) -> str:
        """Sanitiza um nome de arquivo removendo caracteres perigosos.

        Remove .., /, \\ e caracteres especiais, mantendo apenas
        letras, números, underscores, hífens e espaços.

        Args:
            name: Nome original do arquivo.

        Returns:
            Nome sanitizado seguro para uso em paths.
        """
        # Remove path traversal
        sanitized = name.replace("..", "").replace("/", "").replace("\\", "")
        # Remove caracteres especiais, mantém alfanuméricos, underscore, hífen, espaço
        sanitized = re.sub(r"[^\w\s\-]", "", sanitized)
        # Remove espaços múltiplos
        sanitized = re.sub(r"\s+", " ", sanitized).strip()
        # Limita tamanho
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        return sanitized or "report"

    def _get_output_path(
        self, base_name: str, extension: str, db_name: str
    ) -> str:
        """Gera o caminho completo do arquivo de saída.

        Args:
            base_name: Nome base do relatório.
            extension: Extensão do arquivo (ex: 'xlsx').
            db_name: Nome do banco de dados (usado no subdiretório).

        Returns:
            Caminho completo do arquivo.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_base = self.sanitize_filename(base_name)
        safe_db = self.sanitize_filename(db_name)
        sub_dir = os.path.join(self.output_dir, f"{safe_db}_{timestamp}")
        os.makedirs(sub_dir, exist_ok=True)
        return os.path.join(sub_dir, f"{safe_base}_{timestamp}.{extension}")

    def generate_excel(
        self, dataframe: pd.DataFrame, query_name: str, db_name: str
    ) -> Optional[str]:
        """Gera um relatório Excel a partir de um DataFrame.

        Ajusta automaticamente a largura das colunas.

        Args:
            dataframe: DataFrame com os dados.
            query_name: Nome do relatório.
            db_name: Nome do banco de dados.

        Returns:
            Caminho do arquivo gerado ou None em caso de erro.
        """
        if dataframe is None or dataframe.empty:
            logger.warning("DataFrame vazio ou None. Nenhum relatório gerado.")
            return None

        file_path = self._get_output_path(query_name, "xlsx", db_name)
        try:
            writer = pd.ExcelWriter(file_path, engine="openpyxl")
            dataframe.to_excel(writer, index=False, sheet_name="Dados")

            # Auto-ajustar largura das colunas
            workbook = writer.book
            worksheet = writer.sheets["Dados"]
            for column in worksheet.columns:
                max_length = 0
                column_name = column[0].value
                if column_name:
                    max_length = max(max_length, len(str(column_name)))
                for cell in column:
                    try:
                        if cell.value is not None and len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except TypeError:
                        pass
                adjusted_width = (max_length + 2) * 1.2
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

            writer.close()
            logger.info(f"Excel gerado com sucesso: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Erro ao gerar Excel: {e}")
            return None
