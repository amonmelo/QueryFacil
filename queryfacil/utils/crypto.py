"""Módulo de criptografia de senhas usando Fernet."""

import os
import base64
import hashlib
import logging
from typing import Optional

from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


def _get_key_file_path(db_path: str = "db_connections.db") -> str:
    """Retorna o caminho do arquivo de chave Fernet.

    O arquivo .key fica no mesmo diretório do banco SQLite.

    Args:
        db_path: Caminho do banco SQLite usado como referência.

    Returns:
        Caminho absoluto do arquivo .key.
    """
    db_dir = os.path.dirname(os.path.abspath(db_path))
    return os.path.join(db_dir, ".queryfacil.key")


def get_or_create_key(db_path: str = "db_connections.db") -> bytes:
    """Obtém ou cria a chave Fernet para criptografia.

    Na primeira execução, gera uma nova chave e salva em arquivo.
    Nas execuções subsequentes, lê a chave existente.

    Args:
        db_path: Caminho do banco SQLite (usado para localizar o .key).

    Returns:
        Bytes da chave Fernet (base64-encoded).
    """
    key_file = _get_key_file_path(db_path)

    if os.path.exists(key_file):
        try:
            with open(key_file, "rb") as f:
                key = f.read()
            # Valida se a chave é válida para Fernet
            Fernet(key)
            logger.debug("Chave de criptografia carregada com sucesso.")
            return key
        except Exception as e:
            logger.warning(f"Chave existente inválida, gerando nova: {e}")

    # Gerar nova chave
    key = Fernet.generate_key()
    try:
        with open(key_file, "wb") as f:
            f.write(key)
        # Torna o arquivo somente leitura para o dono (Unix)
        try:
            os.chmod(key_file, 0o600)
        except (OSError, AttributeError):
            pass
        logger.info("Nova chave de criptografia gerada e salva.")
    except OSError as e:
        logger.error(f"Não foi possível salvar a chave de criptografia: {e}")
    return key


def _get_fernet(db_path: str = "db_connections.db") -> Fernet:
    """Retorna uma instância de Fernet configurada.

    Args:
        db_path: Caminho do banco SQLite para localizar o .key.

    Returns:
        Instância de Fernet pronta para uso.
    """
    key = get_or_create_key(db_path)
    return Fernet(key)


def encrypt_password(plain_text: str, db_path: str = "db_connections.db") -> bytes:
    """Criptografa uma senha em texto puro.

    Args:
        plain_text: Senha em texto puro.
        db_path: Caminho do banco SQLite para localizar o .key.

    Returns:
        Senha criptografada como bytes (token Fernet).
    """
    if not plain_text:
        return b""
    fernet = _get_fernet(db_path)
    encrypted = fernet.encrypt(plain_text.encode("utf-8"))
    logger.debug("Senha criptografada com sucesso.")
    return encrypted


def decrypt_password(encrypted: bytes, db_path: str = "db_connections.db") -> str:
    """Descriptografa uma senha.

    Suporta migração automática: se o valor não for bytes (texto puro antigo),
    retorna o valor original para permitir re-criptografia posterior.

    Args:
        encrypted: Senha criptografada (bytes) ou texto puro legado.
        db_path: Caminho do banco SQLite para localizar o .key.

    Returns:
        Senha em texto puro.
    """
    if not encrypted:
        return ""

    # Migração: senha antiga em texto puro (str) no SQLite
    if isinstance(encrypted, str):
        logger.warning("Senha legada (texto puro) detectada. Considere re-salvar a conexão.")
        return encrypted

    try:
        fernet = _get_fernet(db_path)
        decrypted = fernet.decrypt(encrypted)
        logger.debug("Senha descriptografada com sucesso.")
        return decrypted.decode("utf-8")
    except Exception as e:
        logger.error(f"Erro ao descriptografar senha: {e}")
        # Se falhar, retorna como string (pode ser legado)
        if isinstance(encrypted, bytes):
            try:
                return encrypted.decode("utf-8")
            except UnicodeDecodeError:
                return ""
        return str(encrypted)


def is_encrypted(value) -> bool:
    """Verifica se um valor parece ser um token Fernet criptografado.

    Args:
        value: Valor a ser verificado.

    Returns:
        True se parece ser um token Fernet, False caso contrário.
    """
    if not isinstance(value, bytes):
        return False
    try:
        # Tokens Fernet são base64-encoded e começam com 'gAAAA'
        decoded = base64.urlsafe_b64decode(value)
        return len(decoded) > 0
    except Exception:
        return False
