"""Testes do ConnectionRepository."""

import pytest
from queryfacil.models.connection import ConnectionRepository


class TestConnectionRepository:
    """Testes unitários para ConnectionRepository."""

    def test_add_connection_success(self, connection_repo, tmp_db):
        """Testa adicionar uma conexão com sucesso."""
        success, error = connection_repo.add(
            name="test_conn",
            host="localhost",
            port=5432,
            dbname="testdb",
            user="testuser",
            password="testpass",
        )
        assert success is True
        assert error is None

    def test_add_duplicate_connection(self, connection_repo):
        """Testa que adicionar conexão duplicada falha."""
        connection_repo.add("dup", "localhost", 5432, "db", "user", "pass")
        success, error = connection_repo.add("dup", "localhost", 5432, "db", "user", "pass")
        assert success is False
        assert "já existe" in error.lower()

    def test_get_all_empty(self, connection_repo):
        """Testa listar conexões quando não há nenhuma."""
        result = connection_repo.get_all()
        assert result == []

    def test_get_all_with_data(self, connection_repo):
        """Testa listar conexões após inserção."""
        connection_repo.add("c1", "host1", 5432, "db1", "u1", "p1")
        connection_repo.add("c2", "host2", 5433, "db2", "u2", "p2")
        result = connection_repo.get_all()
        assert len(result) == 2
        assert result[0]["name"] == "c1"
        assert result[1]["name"] == "c2"

    def test_get_by_name_exists(self, connection_repo):
        """Testa buscar conexão por nome que existe."""
        connection_repo.add("findme", "host", 5432, "db", "user", "pass")
        result = connection_repo.get_by_name("findme")
        assert result is not None
        assert result["host"] == "host"
        assert result["port"] == 5432

    def test_get_by_name_not_exists(self, connection_repo):
        """Testa buscar conexão por nome que não existe."""
        result = connection_repo.get_by_name("nonexistent")
        assert result is None

    def test_update_connection_success(self, connection_repo):
        """Testa atualizar uma conexão com sucesso."""
        connection_repo.add("old", "host", 5432, "db", "user", "pass")
        success, error = connection_repo.update(
            "old", "new", "newhost", 5433, "newdb", "newuser", "newpass"
        )
        assert success is True
        assert error is None

        # Verifica que o nome antigo não existe mais
        assert connection_repo.get_by_name("old") is None
        # Verifica que o novo nome existe
        new_conn = connection_repo.get_by_name("new")
        assert new_conn is not None
        assert new_conn["host"] == "newhost"

    def test_update_duplicate_name(self, connection_repo):
        """Testa que atualizar para nome duplicado falha."""
        connection_repo.add("c1", "h1", 5432, "d1", "u1", "p1")
        connection_repo.add("c2", "h2", 5432, "d2", "u2", "p2")
        success, error = connection_repo.update("c1", "c2", "h3", 5433, "d3", "u3", "p3")
        assert success is False
        assert "já existe" in error.lower()

    def test_delete_connection_success(self, connection_repo):
        """Testa remover uma conexão com sucesso."""
        connection_repo.add("delme", "host", 5432, "db", "user", "pass")
        success, error = connection_repo.delete("delme")
        assert success is True
        assert error is None
        assert connection_repo.get_by_name("delme") is None

    def test_delete_connection_not_exists(self, connection_repo):
        """Testa remover conexão que não existe."""
        success, error = connection_repo.delete("nonexistent")
        assert success is True  # SQLite DELETE sem WHERE match não dá erro

    def test_password_is_encrypted(self, connection_repo):
        """Testa que a senha é armazenada criptografada."""
        connection_repo.add("enc_test", "host", 5432, "db", "user", "secretpass")
        # Acesso direto ao SQLite para verificar
        conn = connection_repo._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM connections WHERE name = ?", ("enc_test",))
        row = cursor.fetchone()
        assert row is not None
        # A senha deve ser bytes (criptografada), não texto puro
        stored_pwd = row["password"]
        assert stored_pwd != "secretpass"
        assert isinstance(stored_pwd, bytes)
