"""Testes do ReportService."""

import os
import pytest
import pandas as pd
from queryfacil.services.report_service import ReportService


class TestReportService:
    """Testes unitários para ReportService."""

    def test_sanitize_filename_normal(self, report_service):
        """Testa sanitização de nome normal."""
        result = report_service.sanitize_filename("meu_relatorio")
        assert result == "meu_relatorio"

    def test_sanitize_filename_path_traversal(self, report_service):
        """Testa que path traversal é removido."""
        assert report_service.sanitize_filename("../../../etc/passwd") == "etcpasswd"
        assert report_service.sanitize_filename("..\\windows\\system32") == "windowssystem32"

    def test_sanitize_filename_special_chars(self, report_service):
        """Testa que caracteres especiais são removidos."""
        result = report_service.sanitize_filename("relatório@#$% teste")
        assert "@" not in result
        assert "#" not in result
        assert "$" not in result
        assert "%" not in result

    def test_sanitize_filename_empty(self, report_service):
        """Testa que nome vazio retorna 'report'."""
        result = report_service.sanitize_filename("")
        assert result == "report"

    def test_sanitize_filename_only_special_chars(self, report_service):
        """Testa que nome só com especiais retorna 'report'."""
        result = report_service.sanitize_filename("@#$%")
        assert result == "report"

    def test_generate_excel_success(self, report_service, sample_dataframe, tmp_path):
        """Testa geração de arquivo Excel com sucesso."""
        path = report_service.generate_excel(sample_dataframe, "teste", "mydb")
        assert path is not None
        assert os.path.exists(path)
        assert path.endswith(".xlsx")

        # Verifica conteúdo básico
        df_read = pd.read_excel(path)
        assert len(df_read) == 3
        assert "id" in df_read.columns

    def test_generate_excel_none_dataframe(self, report_service):
        """Testa que DataFrame None retorna None."""
        path = report_service.generate_excel(None, "teste", "db")
        assert path is None

    def test_generate_excel_empty_dataframe(self, report_service):
        """Testa que DataFrame vazio retorna None."""
        df = pd.DataFrame()
        path = report_service.generate_excel(df, "teste", "db")
        assert path is None

    def test_generate_excel_sanitizes_name(self, report_service, sample_dataframe):
        """Testa que o nome do relatório é sanitizado no caminho do arquivo."""
        path = report_service.generate_excel(
            sample_dataframe, "relatório/../../malicious", "db"
        )
        assert path is not None
        assert "../../" not in path
        assert os.path.exists(path)

    def test_output_dir_created(self, report_service, tmp_path):
        """Testa que o diretório de saída é criado."""
        assert os.path.isdir(report_service.output_dir)
