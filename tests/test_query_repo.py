"""Testes do QueryRepository."""

import pytest
from queryfacil.models.query import QueryRepository, SAVE_OK, SAVE_OVERWRITE_NEEDED, SAVE_ERROR


class TestQueryRepository:
    """Testes unitários para QueryRepository."""

    def test_save_new_query(self, query_repo):
        """Testa salvar uma nova query com sucesso."""
        status, data = query_repo.save("query1", "SELECT * FROM table1")
        assert status == SAVE_OK
        assert data is None

    def test_save_duplicate_without_overwrite(self, query_repo):
        """Testa que salvar query duplicada retorna OVERWRITE_NEEDED."""
        query_repo.save("dup", "SELECT 1")
        status, data = query_repo.save("dup", "SELECT 2")
        assert status == SAVE_OVERWRITE_NEEDED
        assert data == "dup"

    def test_save_duplicate_with_overwrite(self, query_repo):
        """Testa sobrescrever query existente."""
        query_repo.save("ow", "SELECT 1")
        status, data = query_repo.save("ow", "SELECT 2", overwrite=True)
        assert status == SAVE_OK
        assert data is None
        # Verifica que o conteúdo foi atualizado
        text = query_repo.get_by_name("ow")
        assert text == "SELECT 2"

    def test_get_all_empty(self, query_repo):
        """Testa listar queries quando não há nenhuma."""
        result = query_repo.get_all()
        assert result == []

    def test_get_all_with_data(self, query_repo):
        """Testa listar queries após inserção."""
        query_repo.save("q1", "SELECT 1")
        query_repo.save("q2", "SELECT 2")
        result = query_repo.get_all()
        assert len(result) == 2
        names = [r[0] for r in result]
        assert "q1" in names
        assert "q2" in names

    def test_get_by_name_exists(self, query_repo):
        """Testa buscar query por nome que existe."""
        query_repo.save("findme", "SELECT * FROM users")
        text = query_repo.get_by_name("findme")
        assert text == "SELECT * FROM users"

    def test_get_by_name_not_exists(self, query_repo):
        """Testa buscar query por nome que não existe."""
        text = query_repo.get_by_name("nonexistent")
        assert text is None

    def test_delete_query_success(self, query_repo):
        """Testa remover uma query com sucesso."""
        query_repo.save("delme", "SELECT 1")
        success, error = query_repo.delete("delme")
        assert success is True
        assert error is None
        assert query_repo.get_by_name("delme") is None

    def test_delete_query_not_exists(self, query_repo):
        """Testa remover query que não existe."""
        success, error = query_repo.delete("ghost")
        assert success is True  # SQLite DELETE sem WHERE match não dá erro

    def test_save_preserves_unicode(self, query_repo):
        """Testa que queries com caracteres especiais são salvas corretamente."""
        query_text = "SELECT nome, descrição FROM tabela WHERE id = 1"
        status, _ = query_repo.save("unicode_test", query_text)
        assert status == SAVE_OK
        retrieved = query_repo.get_by_name("unicode_test")
        assert retrieved == query_text
