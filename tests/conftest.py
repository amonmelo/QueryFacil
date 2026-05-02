"""Fixtures compartilhadas para os testes do QueryFacil."""

import os
import pytest
import sqlite3
from unittest.mock import MagicMock, patch

from queryfacil.models.connection import ConnectionRepository
from queryfacil.models.query import QueryRepository
from queryfacil.services.db_manager import DBManager
from queryfacil.services.postgres_service import PostgresService
from queryfacil.services.report_service import ReportService


@pytest.fixture
def tmp_db(tmp_path):
    """Cria um banco SQLite temporário para testes.

    Args:
        tmp_path: Path temporário do pytest.

    Yields:
        Caminho do banco SQLite temporário.
    """
    db_path = str(tmp_path / "test_db.db")
    yield db_path
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)
    key_file = os.path.join(os.path.dirname(db_path), ".queryfacil.key")
    if os.path.exists(key_file):
        os.remove(key_file)


@pytest.fixture
def connection_repo(tmp_db):
    """Cria um ConnectionRepository com banco temporário.

    Args:
        tmp_db: Fixture de banco temporário.

    Yields:
        ConnectionRepository configurado.
    """
    repo = ConnectionRepository(tmp_db)
    yield repo
    repo.close()


@pytest.fixture
def query_repo(tmp_db):
    """Cria um QueryRepository com banco temporário.

    Args:
        tmp_db: Fixture de banco temporário.

    Yields:
        QueryRepository configurado.
    """
    repo = QueryRepository(tmp_db)
    yield repo
    repo.close()


@pytest.fixture
def db_manager(tmp_db):
    """Cria um DBManager com banco temporário.

    Args:
        tmp_db: Fixture de banco temporário.

    Yields:
        DBManager configurado.
    """
    manager = DBManager(tmp_db)
    yield manager
    manager.close()


@pytest.fixture
def postgres_service():
    """Cria um PostgresService.

    Yields:
        PostgresService sem conexão.
    """
    yield PostgresService()


@pytest.fixture
def report_service(tmp_path):
    """Cria um ReportService com diretório temporário.

    Args:
        tmp_path: Path temporário do pytest.

    Yields:
        ReportService configurado.
    """
    output_dir = str(tmp_path / "relatorios")
    yield ReportService(output_dir)


@pytest.fixture
def mock_psycopg2():
    """Mock do módulo psycopg2 para testes sem banco real.

    Yields:
        MagicMock do psycopg2.
    """
    with patch("queryfacil.services.postgres_service.psycopg2") as mock:
        yield mock


@pytest.fixture
def sample_dataframe():
    """Cria um DataFrame de exemplo para testes.

    Yields:
        DataFrame pandas com dados de exemplo.
    """
    import pandas as pd
    return pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "value": [10.5, 20.3, 30.1],
    })
