"""Repositório de queries salvas (SQLite).

Gerencia CRUD de queries armazenadas localmente.
Sem dependência de GUI (sem QMessageBox).
"""

import sqlite3
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)

# Constantes de status para save_query
SAVE_OK = "SAVE_OK"
SAVE_OVERWRITE_NEEDED = "SAVE_OVERWRITE_NEEDED"
SAVE_ERROR = "SAVE_ERROR"


class QueryRepository:
    """Repositório para gerenciar queries salvas no SQLite.

    Attributes:
        db_path: Caminho do arquivo SQLite.
    """

    def __init__(self, db_path: str = "db_connections.db") -> None:
        """Inicializa o repositório e cria tabelas se necessário.

        Args:
            db_path: Caminho do banco SQLite.
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Retorna a conexão SQLite, recriando se necessário.

        Returns:
            Conexão SQLite ativa.
        """
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def _init_db(self) -> None:
        """Cria a tabela de queries salvas se não existir."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    query_text TEXT NOT NULL
                )
            """)
            conn.commit()
            logger.info("Tabela 'saved_queries' inicializada com sucesso.")
        except sqlite3.Error as e:
            logger.error(f"Erro ao inicializar tabela saved_queries: {e}")

    def save(
        self, name: str, query_text: str, overwrite: bool = False
    ) -> Tuple[str, Optional[str]]:
        """Salva uma query.

        Se já existe uma query com o mesmo nome, retorna SAVE_OVERWRITE_NEEDED
        para que a View decida se pergunta ao usuário.

        Args:
            name: Nome da query.
            query_text: Texto SQL da query.
            overwrite: Se True, sobrescreve sem perguntar.

        Returns:
            Tupla (status, mensagem_erro).
            status pode ser SAVE_OK, SAVE_OVERWRITE_NEEDED ou SAVE_ERROR.
        """
        try:
            conn = self._get_conn()
            cursor = conn.cursor()

            # Verifica se já existe
            cursor.execute("SELECT id FROM saved_queries WHERE name = ?", (name,))
            if cursor.fetchone():
                if not overwrite:
                    logger.info(f"Query '{name}' já existe. Sobrescrita necessária.")
                    return SAVE_OVERWRITE_NEEDED, name
                else:
                    cursor.execute(
                        "UPDATE saved_queries SET query_text = ? WHERE name = ?",
                        (query_text, name),
                    )
                    conn.commit()
                    logger.info(f"Query '{name}' atualizada (overwrite).")
                    return SAVE_OK, None

            cursor.execute(
                "INSERT INTO saved_queries (name, query_text) VALUES (?, ?)",
                (name, query_text),
            )
            conn.commit()
            logger.info(f"Query '{name}' salva com sucesso.")
            return SAVE_OK, None
        except sqlite3.Error as e:
            msg = f"Erro ao salvar query: {e}"
            logger.error(msg)
            return SAVE_ERROR, msg

    def get_all(self) -> List[Tuple[str, str]]:
        """Retorna todas as queries salvas.

        Returns:
            Lista de tuplas (nome, texto_query) ordenadas por nome.
        """
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT name, query_text FROM saved_queries ORDER BY name")
            return [(row["name"], row["query_text"]) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Erro ao listar queries: {e}")
            return []

    def get_by_name(self, name: str) -> Optional[str]:
        """Busca uma query pelo nome.

        Args:
            name: Nome da query.

        Returns:
            Texto SQL da query ou None se não encontrada.
        """
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT query_text FROM saved_queries WHERE name = ?", (name,)
            )
            row = cursor.fetchone()
            return row["query_text"] if row else None
        except sqlite3.Error as e:
            logger.error(f"Erro ao buscar query por nome: {e}")
            return None

    def delete(self, name: str) -> Tuple[bool, Optional[str]]:
        """Remove uma query pelo nome.

        Args:
            name: Nome da query a remover.

        Returns:
            Tupla (sucesso, mensagem_erro).
        """
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM saved_queries WHERE name = ?", (name,))
            conn.commit()
            logger.info(f"Query '{name}' removida com sucesso.")
            return True, None
        except sqlite3.Error as e:
            msg = f"Erro ao remover query: {e}"
            logger.error(msg)
            return False, msg

    def close(self) -> None:
        """Fecha a conexão SQLite."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Conexão SQLite (queries) fechada.")
