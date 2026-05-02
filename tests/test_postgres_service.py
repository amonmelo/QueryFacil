"""Testes do PostgresService."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from queryfacil.services.postgres_service import PostgresService


class TestPostgresService:
    """Testes unitários para PostgresService."""

    def test_set_connection_config(self, postgres_service):
        """Testa definir configuração de conexão."""
        config = {
            "host": "localhost",
            "port": 5432,
            "dbname": "testdb",
            "user": "testuser",
            "password": "testpass",
        }
        postgres_service.set_connection_config(config)
        assert postgres_service.connection_config == config

    def test_connect_no_config(self, postgres_service):
        """Testa conectar sem configuração definida."""
        success, error, conn = postgres_service.connect()
        assert success is False
        assert "configuração" in error.lower()
        assert conn is None

    @patch("queryfacil.services.postgres_service.psycopg2")
    def test_connect_success(self, mock_psycopg2, postgres_service):
        """Testa conexão bem-sucedida."""
        mock_conn = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn

        postgres_service.set_connection_config({
            "host": "localhost", "port": 5432, "dbname": "db",
            "user": "user", "password": "pass",
        })

        success, error, conn = postgres_service.connect()
        assert success is True
        assert error is None
        assert conn == mock_conn
        mock_psycopg2.connect.assert_called_once()

    @patch("queryfacil.services.postgres_service.psycopg2")
    def test_connect_failure(self, mock_psycopg2, postgres_service):
        """Testa falha na conexão."""
        mock_psycopg2.Error = Exception
        mock_psycopg2.connect.side_effect = Exception("Connection refused")

        postgres_service.set_connection_config({
            "host": "badhost", "port": 5432, "dbname": "db",
            "user": "user", "password": "pass",
        })

        success, error, conn = postgres_service.connect()
        assert success is False
        assert "Connection refused" in error
        assert conn is None

    @patch("queryfacil.services.postgres_service.psycopg2")
    def test_execute_select(self, mock_psycopg2, postgres_service):
        """Testa execução de query SELECT."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "Alice"), (2, "Bob")]
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn

        postgres_service.set_connection_config({
            "host": "localhost", "port": 5432, "dbname": "db",
            "user": "user", "password": "pass",
        })

        df, error = postgres_service.execute_query("SELECT id, name FROM users")
        assert error is None
        assert df is not None
        assert len(df) == 2
        assert "id" in df.columns
        assert "name" in df.columns
        mock_conn.close.assert_called_once()

    @patch("queryfacil.services.postgres_service.psycopg2")
    def test_execute_dml(self, mock_psycopg2, postgres_service):
        """Testa execução de query DML (INSERT/UPDATE/DELETE)."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # fetchall/description raises ProgrammingError for DML
        mock_psycopg2.ProgrammingError = type("ProgrammingError", (Exception,), {})
        mock_cursor.description = None
        mock_cursor.fetchall.side_effect = mock_psycopg2.ProgrammingError("no results")
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn

        postgres_service.set_connection_config({
            "host": "localhost", "port": 5432, "dbname": "db",
            "user": "user", "password": "pass",
        })

        df, error = postgres_service.execute_query("INSERT INTO t VALUES (1)")
        assert df is None
        assert "sem dados" in error.lower()
        mock_conn.commit.assert_called_once()

    @patch("queryfacil.services.postgres_service.psycopg2")
    def test_execute_error(self, mock_psycopg2, postgres_service):
        """Testa tratamento de erro na execução."""
        mock_psycopg2.Error = type("PgError", (Exception,), {})
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = mock_psycopg2.Error("syntax error")
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn

        postgres_service.set_connection_config({
            "host": "localhost", "port": 5432, "dbname": "db",
            "user": "user", "password": "pass",
        })

        df, error = postgres_service.execute_query("INVALID SQL")
        assert df is None
        assert "syntax error" in error

    @patch("queryfacil.services.postgres_service.psycopg2")
    def test_statement_timeout_in_options(self, mock_psycopg2, postgres_service):
        """Testa que statement_timeout é passado nas opções de conexão."""
        mock_conn = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn

        postgres_service.set_connection_config({
            "host": "localhost", "port": 5432, "dbname": "db",
            "user": "user", "password": "pass",
        })

        postgres_service.connect()
        call_kwargs = mock_psycopg2.connect.call_args[1]
        assert "statement_timeout" in call_kwargs["options"]

    def test_is_destructive_drop(self, postgres_service):
        """Testa detecção de DROP."""
        assert postgres_service.is_destructive_query("DROP TABLE users;") is True

    def test_is_destructive_truncate(self, postgres_service):
        """Testa detecção de TRUNCATE."""
        assert postgres_service.is_destructive_query("TRUNCATE TABLE users;") is True

    def test_is_destructive_alter(self, postgres_service):
        """Testa detecção de ALTER."""
        assert postgres_service.is_destructive_query("ALTER TABLE users ADD COLUMN x INT;") is True

    def test_is_destructive_delete_no_where(self, postgres_service):
        """Testa detecção de DELETE sem WHERE."""
        assert postgres_service.is_destructive_query("DELETE FROM users;") is True

    def test_is_destructive_update_no_where(self, postgres_service):
        """Testa detecção de UPDATE sem WHERE."""
        assert postgres_service.is_destructive_query("UPDATE users SET name = 'x';") is True

    def test_is_not_destructive_select(self, postgres_service):
        """Testa que SELECT não é destrutivo."""
        assert postgres_service.is_destructive_query("SELECT * FROM users;") is False

    def test_is_not_destructive_delete_with_where(self, postgres_service):
        """Testa que DELETE com WHERE não é considerado destrutivo."""
        assert postgres_service.is_destructive_query("DELETE FROM users WHERE id = 1;") is False

    def test_is_not_destructive_update_with_where(self, postgres_service):
        """Testa que UPDATE com WHERE não é considerado destrutivo."""
        assert postgres_service.is_destructive_query("UPDATE users SET name = 'x' WHERE id = 1;") is False

    def test_is_not_destructive_empty(self, postgres_service):
        """Testa que query vazia não é destrutiva."""
        assert postgres_service.is_destructive_query("") is False

    def test_is_not_destructive_insert(self, postgres_service):
        """Testa que INSERT não é destrutivo."""
        assert postgres_service.is_destructive_query("INSERT INTO users VALUES (1);") is False

    def test_execute_query_no_config(self, postgres_service):
        """Testa executar query sem configuração."""
        df, error = postgres_service.execute_query("SELECT 1")
        assert df is None
        assert "conexão" in error.lower()
