"""Gerenciador de banco de dados — orquestra repositórios sem GUI.

Coordena ConnectionRepository e QueryRepository, fornecendo
uma interface unificada para a camada de visualização.
"""

import logging
from typing import Optional, Tuple, List, Dict, Any

from queryfacil.models.connection import ConnectionRepository
from queryfacil.models.query import QueryRepository, SAVE_OK, SAVE_OVERWRITE_NEEDED, SAVE_ERROR
from queryfacil.utils.crypto import decrypt_password

logger = logging.getLogger(__name__)


class DBManager:
    """Orquestra ConnectionRepository e QueryRepository.

    Sem dependência de GUI. Métodos retornam tuplas de status.

    Attributes:
        connection_repo: Repositório de conexões.
        query_repo: Repositório de queries.
        current_db_config: Configuração da conexão atualmente selecionada.
    """

    def __init__(self, db_path: str = "db_connections.db") -> None:
        """Inicializa o gerenciador com os repositórios.

        Args:
            db_path: Caminho do banco SQLite.
        """
        self.connection_repo = ConnectionRepository(db_path)
        self.query_repo = QueryRepository(db_path)
        self.current_db_config: Optional[Dict[str, Any]] = None

    # --- Connection Management ---

    def test_connection(
        self, host: str, port: int, dbname: str, user: str, password: str
    ) -> Tuple[bool, Optional[str]]:
        """Testa uma conexão PostgreSQL.

        Args:
            host: Host do servidor.
            port: Porta.
            dbname: Nome do banco.
            user: Usuário.
            password: Senha em texto puro.

        Returns:
            Tupla (sucesso, mensagem_erro).
        """
        return self.connection_repo.test_connection(host, port, dbname, user, password)

    def add_connection(
        self, name: str, host: str, port: int, dbname: str, user: str, password: str
    ) -> Tuple[bool, Optional[str]]:
        """Adiciona e testa uma nova conexão.

        Args:
            name: Nome da conexão.
            host: Host.
            port: Porta.
            dbname: Nome do banco.
            user: Usuário.
            password: Senha.

        Returns:
            Tupla (sucesso, mensagem_erro).
        """
        success, error = self.test_connection(host, port, dbname, user, password)
        if not success:
            return False, f"Teste de conexão falhou: {error}"
        return self.connection_repo.add(name, host, port, dbname, user, password)

    def update_connection(
        self,
        old_name: str,
        name: str,
        host: str,
        port: int,
        dbname: str,
        user: str,
        password: str,
    ) -> Tuple[bool, Optional[str]]:
        """Atualiza uma conexão existente.

        Args:
            old_name: Nome atual.
            name: Novo nome.
            host: Novo host.
            port: Nova porta.
            dbname: Novo nome do banco.
            user: Novo usuário.
            password: Nova senha.

        Returns:
            Tupla (sucesso, mensagem_erro).
        """
        success, error = self.test_connection(host, port, dbname, user, password)
        if not success:
            return False, f"Teste de conexão falhou: {error}"
        return self.connection_repo.update(old_name, name, host, port, dbname, user, password)

    def delete_connection(self, name: str) -> Tuple[bool, Optional[str]]:
        """Remove uma conexão.

        Args:
            name: Nome da conexão.

        Returns:
            Tupla (sucesso, mensagem_erro).
        """
        return self.connection_repo.delete(name)

    def get_connections(self) -> List[Dict[str, Any]]:
        """Retorna todas as conexões cadastradas.

        Returns:
            Lista de dicionários com dados das conexões.
        """
        return self.connection_repo.get_all()

    def get_connection_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Busca uma conexão pelo nome e define como atual.

        Args:
            name: Nome da conexão.

        Returns:
            Dicionário com configuração (senha descriptografada) ou None.
        """
        conn_data = self.connection_repo.get_by_name(name)
        if conn_data:
            # Descriptografa a senha para uso
            config = {
                "host": conn_data["host"],
                "port": conn_data["port"],
                "dbname": conn_data["dbname"],
                "user": conn_data["user"],
                "password": decrypt_password(conn_data["password"]),
            }
            self.current_db_config = config
            return config
        return None

    # --- Query Management ---

    def save_query(self, name: str, query_text: str, overwrite: bool = False) -> Tuple[str, Optional[str]]:
        """Salva uma query.

        Args:
            name: Nome da query.
            query_text: Texto SQL.
            overwrite: Se True, sobrescreve sem perguntar.

        Returns:
            Tupla (status, dados_extras).
            Status: SAVE_OK, SAVE_OVERWRITE_NEEDED ou SAVE_ERROR.
        """
        return self.query_repo.save(name, query_text, overwrite=overwrite)

    def get_saved_queries(self) -> List[Tuple[str, str]]:
        """Retorna todas as queries salvas.

        Returns:
            Lista de tuplas (nome, texto).
        """
        return self.query_repo.get_all()

    def get_query_by_name(self, name: str) -> Optional[str]:
        """Busca uma query pelo nome.

        Args:
            name: Nome da query.

        Returns:
            Texto SQL ou None.
        """
        return self.query_repo.get_by_name(name)

    def delete_query(self, name: str) -> Tuple[bool, Optional[str]]:
        """Remove uma query.

        Args:
            name: Nome da query.

        Returns:
            Tupla (sucesso, mensagem_erro).
        """
        return self.query_repo.delete(name)

    def close(self) -> None:
        """Fecha todas as conexões SQLite."""
        self.connection_repo.close()
        self.query_repo.close()
