"""Serviço de conexão e execução de queries PostgreSQL."""

import logging
from typing import Optional, Tuple

import pandas as pd
import psycopg2
from psycopg2 import Error as PgError

from queryfacil.config import (
    DEFAULT_ENCODING,
    DEFAULT_QUERY_TIMEOUT,
    DEFAULT_CONNECT_TIMEOUT,
)

logger = logging.getLogger(__name__)


class PostgresService:
    """Serviço para conectar e executar queries no PostgreSQL.

    Attributes:
        connection_config: Configuração da conexão atual.
    """

    def __init__(self) -> None:
        """Inicializa o serviço sem conexão ativa."""
        self.connection_config: Optional[dict] = None

    def set_connection_config(self, config: dict) -> None:
        """Define a configuração de conexão.

        Args:
            config: Dicionário com host, port, dbname, user, password.
        """
        self.connection_config = config

    def connect(self) -> Tuple[bool, Optional[str], Optional[object]]:
        """Estabelece uma conexão com o PostgreSQL.

        Uses statement_timeout and connect_timeout from config.

        Returns:
            Tupla (sucesso, mensagem_erro, conexao_psycopg2).
        """
        if not self.connection_config:
            return False, "Nenhuma configuração de conexão definida.", None

        conn = None
        try:
            timeout_ms = DEFAULT_QUERY_TIMEOUT * 1000
            conn = psycopg2.connect(
                host=self.connection_config["host"],
                port=self.connection_config["port"],
                database=self.connection_config["dbname"],
                user=self.connection_config["user"],
                password=self.connection_config["password"],
                options=(
                    f"-c client_encoding={DEFAULT_ENCODING} "
                    f"-c statement_timeout={timeout_ms}"
                ),
                connect_timeout=DEFAULT_CONNECT_TIMEOUT,
            )
            logger.info(
                f"Conectado ao PostgreSQL: "
                f"{self.connection_config['user']}@{self.connection_config['host']}:"
                f"{self.connection_config['port']}/{self.connection_config['dbname']}"
            )
            return True, None, conn
        except psycopg2.Error as e:
            msg = str(e)
            logger.error(f"Erro de conexão PostgreSQL: {msg}")
            return False, msg, None
        except Exception as e:
            msg = str(e)
            logger.error(f"Erro inesperado na conexão: {msg}")
            return False, msg, None

    def execute_query(self, query: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """Executa uma query SQL e retorna os resultados.

        Para queries SELECT, retorna um DataFrame.
        Para DML/DDL, retorna None com mensagem de sucesso.

        Args:
            query: Query SQL a executar.

        Returns:
            Tupla (dataframe_ou_None, mensagem_erro).
            Se dataframe é None e erro é None, foi DML/DDL com sucesso.
        """
        if not self.connection_config:
            return None, "Nenhuma conexão selecionada."

        import psycopg2

        conn = None
        try:
            success, error, conn = self.connect()
            if not success or conn is None:
                return None, error or "Falha na conexão."

            cursor = conn.cursor()
            cursor.execute(query)

            # Tenta buscar resultados (SELECT)
            try:
                if cursor.description is None:
                    raise psycopg2.ProgrammingError("no results")
                columns = [desc[0] for desc in cursor.description]
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=columns)
                logger.info(f"SELECT executado com sucesso. {len(df)} linhas.")
                return df, None
            except (psycopg2.ProgrammingError, AttributeError):
                # DML/DDL — sem resultados para buscar
                conn.commit()
                logger.info("Comando SQL (DML/DDL) executado com sucesso.")
                return None, "Comando SQL executado com sucesso (sem dados retornados)."

        except psycopg2.Error as e:
            msg = f"Erro ao executar query: {e}"
            logger.error(msg)
            return None, msg
        except Exception as e:
            msg = f"Erro inesperado: {e}"
            logger.error(msg)
            return None, msg
        finally:
            if conn:
                conn.close()

    def is_destructive_query(self, query: str) -> bool:
        """Verifica se a query é potencialmente destrutiva.

        Checa se a query começa com palavras-chave perigosas
        (case-insensitive): DROP, TRUNCATE, DELETE, ALTER, UPDATE sem WHERE.

        Args:
            query: Texto SQL da query.

        Returns:
            True se a query é potencialmente destrutiva.
        """
        stripped = query.strip()
        if not stripped:
            return False

        upper = stripped.upper()

        # DDL destrutivo
        dangerous_starts = ["DROP ", "DROP\t", "TRUNCATE ", "TRUNCATE\t", "ALTER "]
        for start in dangerous_starts:
            if upper.startswith(start):
                return True

        # DELETE sem WHERE
        if upper.startswith("DELETE ") or upper.startswith("DELETE\t"):
            if "WHERE" not in upper:
                return True

        # UPDATE sem WHERE
        if upper.startswith("UPDATE ") or upper.startswith("UPDATE\t"):
            if "WHERE" not in upper:
                return True

        return False
