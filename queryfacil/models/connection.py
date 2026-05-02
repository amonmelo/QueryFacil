"""Repositório de conexões de banco de dados (SQLite).

Gerencia CRUD de conexões PostgreSQL armazenadas localmente.
Sem dependência de GUI (sem QMessageBox).
"""

import sqlite3
import logging
from typing import Optional, Tuple, List, Dict, Any

from queryfacil.utils.crypto import encrypt_password, decrypt_password, is_encrypted

logger = logging.getLogger(__name__)


class ConnectionRepository:
    """Repositório para gerenciar conexões no SQLite.

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
        """Cria as tabelas de conexões se não existirem."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    host TEXT NOT NULL,
                    port INTEGER NOT NULL,
                    dbname TEXT NOT NULL,
                    user TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            conn.commit()
            logger.info("Tabela 'connections' inicializada com sucesso.")
        except sqlite3.Error as e:
            logger.error(f"Erro ao inicializar tabela connections: {e}")

    def _migrate_password(self, password_value: Any) -> bytes:
        """Migra senhas em texto puro para criptografadas.

        Args:
            password_value: Valor da senha (pode ser str legado ou bytes).

        Returns:
            Senha criptografada em bytes.
        """
        if isinstance(password_value, str):
            # Senha legada em texto puro — criptografa na leitura
            encrypted = encrypt_password(password_value, self.db_path)
            logger.info("Senha legada migrada para criptografia.")
            return encrypted
        if isinstance(password_value, bytes):
            if is_encrypted(password_value):
                return password_value
            # Bytes não-criptografados (legado)
            try:
                plain = password_value.decode("utf-8")
                return encrypt_password(plain, self.db_path)
            except UnicodeDecodeError:
                return password_value
        return encrypt_password(str(password_value), self.db_path)

    def add(
        self, name: str, host: str, port: int, dbname: str, user: str, password: str
    ) -> Tuple[bool, Optional[str]]:
        """Adiciona uma nova conexão.

        A senha é criptografada antes de ser armazenada.

        Args:
            name: Nome da conexão.
            host: Host do servidor PostgreSQL.
            port: Porta do servidor.
            dbname: Nome do banco de dados.
            user: Usuário.
            password: Senha em texto puro.

        Returns:
            Tupla (sucesso, mensagem_erro). erro é None em caso de sucesso.
        """
        encrypted_pwd = encrypt_password(password, self.db_path)
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO connections (name, host, port, dbname, user, password)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (name, host, port, dbname, user, encrypted_pwd),
            )
            conn.commit()
            logger.info(f"Conexão '{name}' adicionada com sucesso.")
            return True, None
        except sqlite3.IntegrityError:
            msg = f"Já existe uma conexão com o nome '{name}'."
            logger.warning(msg)
            return False, msg
        except sqlite3.Error as e:
            msg = f"Erro ao adicionar conexão: {e}"
            logger.error(msg)
            return False, msg

    def update(
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
            old_name: Nome atual da conexão.
            name: Novo nome.
            host: Novo host.
            port: Nova porta.
            dbname: Novo nome do banco.
            user: Novo usuário.
            password: Nova senha em texto puro.

        Returns:
            Tupla (sucesso, mensagem_erro).
        """
        encrypted_pwd = encrypt_password(password, self.db_path)
        try:
            conn = self._get_conn()
            cursor = conn.cursor()

            # Verifica unicidade do novo nome se alterado
            if old_name != name:
                cursor.execute(
                    "SELECT id FROM connections WHERE name = ?", (name,)
                )
                if cursor.fetchone():
                    msg = f"Já existe uma conexão com o nome '{name}'."
                    logger.warning(msg)
                    return False, msg

            cursor.execute(
                """UPDATE connections
                   SET name = ?, host = ?, port = ?, dbname = ?, user = ?, password = ?
                   WHERE name = ?""",
                (name, host, port, dbname, user, encrypted_pwd, old_name),
            )
            conn.commit()
            logger.info(f"Conexão '{old_name}' atualizada para '{name}'.")
            return True, None
        except sqlite3.Error as e:
            msg = f"Erro ao atualizar conexão: {e}"
            logger.error(msg)
            return False, msg

    def delete(self, name: str) -> Tuple[bool, Optional[str]]:
        """Remove uma conexão pelo nome.

        Args:
            name: Nome da conexão a remover.

        Returns:
            Tupla (sucesso, mensagem_erro).
        """
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM connections WHERE name = ?", (name,))
            conn.commit()
            logger.info(f"Conexão '{name}' removida com sucesso.")
            return True, None
        except sqlite3.Error as e:
            msg = f"Erro ao remover conexão: {e}"
            logger.error(msg)
            return False, msg

    def get_all(self) -> List[Dict[str, Any]]:
        """Retorna todas as conexões cadastradas.

        Migra senhas legadas para criptografia durante a leitura.

        Returns:
            Lista de dicionários com dados das conexões.
        """
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, host, port, dbname, user, password FROM connections"
            )
            rows = cursor.fetchall()
            results = []
            for row in rows:
                pwd_value = row["password"]
                migrated_pwd = self._migrate_password(pwd_value)
                # Atualiza no banco se migrou
                if migrated_pwd != pwd_value:
                    cursor.execute(
                        "UPDATE connections SET password = ? WHERE id = ?",
                        (migrated_pwd, row["id"]),
                    )
                    conn.commit()

                results.append(
                    {
                        "id": row["id"],
                        "name": row["name"],
                        "host": row["host"],
                        "port": row["port"],
                        "dbname": row["dbname"],
                        "user": row["user"],
                        "password": migrated_pwd,
                    }
                )
            return results
        except sqlite3.Error as e:
            logger.error(f"Erro ao listar conexões: {e}")
            return []

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Busca uma conexão pelo nome.

        Migra senha legada se necessário.

        Args:
            name: Nome da conexão.

        Returns:
            Dicionário com dados da conexão ou None se não encontrada.
        """
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, host, port, dbname, user, password FROM connections WHERE name = ?",
                (name,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            pwd_value = row["password"]
            migrated_pwd = self._migrate_password(pwd_value)
            if migrated_pwd != pwd_value:
                cursor.execute(
                    "UPDATE connections SET password = ? WHERE id = ?",
                    (migrated_pwd, row["id"]),
                )
                conn.commit()

            return {
                "id": row["id"],
                "name": row["name"],
                "host": row["host"],
                "port": row["port"],
                "dbname": row["dbname"],
                "user": row["user"],
                "password": migrated_pwd,
            }
        except sqlite3.Error as e:
            logger.error(f"Erro ao buscar conexão por nome: {e}")
            return None

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
        import psycopg2
        from queryfacil.config import DEFAULT_ENCODING, DEFAULT_CONNECT_TIMEOUT

        conn = None
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=dbname,
                user=user,
                password=password,
                options=f"-c client_encoding={DEFAULT_ENCODING}",
                connect_timeout=DEFAULT_CONNECT_TIMEOUT,
            )
            logger.info(f"Teste de conexão OK para {user}@{host}:{port}/{dbname}")
            return True, None
        except psycopg2.Error as e:
            msg = str(e)
            logger.error(f"Teste de conexão falhou: {msg}")
            return False, msg
        except Exception as e:
            msg = str(e)
            logger.error(f"Erro inesperado no teste de conexão: {msg}")
            return False, msg
        finally:
            if conn:
                conn.close()

    def close(self) -> None:
        """Fecha a conexão SQLite."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Conexão SQLite fechada.")
