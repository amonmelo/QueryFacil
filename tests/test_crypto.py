"""Testes do módulo de criptografia."""

import os
import pytest
from queryfacil.utils.crypto import (
    encrypt_password,
    decrypt_password,
    get_or_create_key,
    is_encrypted,
)


class TestCrypto:
    """Testes unitários para o módulo crypto."""

    def test_encrypt_decrypt_roundtrip(self, tmp_db):
        """Testa que criptografar e descriptografar retorna o valor original."""
        original = "minha_senha_secreta_123"
        encrypted = encrypt_password(original, tmp_db)
        decrypted = decrypt_password(encrypted, tmp_db)
        assert decrypted == original

    def test_encrypt_returns_bytes(self, tmp_db):
        """Testa que encrypt_password retorna bytes."""
        result = encrypt_password("senha", tmp_db)
        assert isinstance(result, bytes)

    def test_decrypt_empty_bytes(self, tmp_db):
        """Testa que descriptografar bytes vazios retorna string vazia."""
        result = decrypt_password(b"", tmp_db)
        assert result == ""

    def test_encrypt_empty_string(self, tmp_db):
        """Testa que criptografar string vazia retorna bytes vazios."""
        result = encrypt_password("", tmp_db)
        assert result == b""

    def test_decrypt_unicode_password(self, tmp_db):
        """Testa criptografia de senha com caracteres unicode."""
        original = "senha_com_çãéíóú@#$%"
        encrypted = encrypt_password(original, tmp_db)
        decrypted = decrypt_password(encrypted, tmp_db)
        assert decrypted == original

    def test_decrypt_long_password(self, tmp_db):
        """Testa criptografia de senha longa."""
        original = "a" * 1000
        encrypted = encrypt_password(original, tmp_db)
        decrypted = decrypt_password(encrypted, tmp_db)
        assert decrypted == original

    def test_key_persistence(self, tmp_db):
        """Testa que a chave é persistida e reutilizada."""
        key1 = get_or_create_key(tmp_db)
        key2 = get_or_create_key(tmp_db)
        assert key1 == key2

    def test_key_file_created(self, tmp_db):
        """Testa que o arquivo de chave é criado."""
        key = get_or_create_key(tmp_db)
        key_file = os.path.join(os.path.dirname(tmp_db), ".queryfacil.key")
        assert os.path.exists(key_file)

        with open(key_file, "rb") as f:
            stored_key = f.read()
        assert stored_key == key

    def test_is_encrypted_true(self, tmp_db):
        """Testa que is_encrypted retorna True para token Fernet."""
        encrypted = encrypt_password("test", tmp_db)
        assert is_encrypted(encrypted) is True

    def test_is_encrypted_false_string(self):
        """Testa que is_encrypted retorna False para string."""
        assert is_encrypted("texto_puro") is False

    def test_is_encrypted_false_empty(self):
        """Testa que is_encrypted retorna False para bytes vazios."""
        assert is_encrypted(b"") is False

    def test_legacy_string_password(self, tmp_db):
        """Testa que senha legada (string) é retornada como texto puro."""
        legacy = "senha_antiga_em_texto"
        result = decrypt_password(legacy, tmp_db)
        assert result == "senha_antiga_em_texto"

    def test_different_passwords_different_encrypted(self, tmp_db):
        """Testa que senhas diferentes produzem tokens diferentes."""
        enc1 = encrypt_password("senha1", tmp_db)
        enc2 = encrypt_password("senha2", tmp_db)
        assert enc1 != enc2

    def test_same_password_decrypts_consistently(self, tmp_db):
        """Testa que mesma senha criptografada duas vezes descriptografa igual."""
        enc1 = encrypt_password("mesma_senha", tmp_db)
        enc2 = encrypt_password("mesma_senha", tmp_db)
        # Fernet usa timestamp — tokens são diferentes, mas descriptografam igual
        assert enc1 != enc2  # timestamp faz tokens serem diferentes
        assert decrypt_password(enc1, tmp_db) == decrypt_password(enc2, tmp_db) == "mesma_senha"
