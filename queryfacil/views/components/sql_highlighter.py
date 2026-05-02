"""Syntax Highlighter para SQL no QTextEdit.

Destaca keywords, strings, números e comentários com cores diferentes.
"""

import re
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont


# Formatos de destaque
class SQLFormats:
    """Formatos de cor para destaque de sintaxe SQL."""

    @staticmethod
    def keyword_format() -> QTextCharFormat:
        """Retorna formato para palavras-chave SQL (azul bold).

        Returns:
            QTextCharFormat configurado para keywords.
        """
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#0000FF"))
        fmt.setFontWeight(QFont.Bold)
        return fmt

    @staticmethod
    def string_format() -> QTextCharFormat:
        """Retorna formato para strings (verde).

        Returns:
            QTextCharFormat configurado para strings.
        """
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#008000"))
        return fmt

    @staticmethod
    def number_format() -> QTextCharFormat:
        """Retorna formato para números (laranja).

        Returns:
            QTextCharFormat configurado para números.
        """
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#FF8C00"))
        return fmt

    @staticmethod
    def comment_format() -> QTextCharFormat:
        """Retorna formato para comentários (cinza itálico).

        Returns:
            QTextCharFormat configurado para comentários.
        """
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#808080"))
        fmt.setFontItalic(True)
        return fmt


class SQLHighlighter(QSyntaxHighlighter):
    """Highlighter de sintaxe SQL para QTextEdit.

    Attributes:
        keywords: Conjunto de palavras-chave SQL.
        rules: Lista de regras (regex, formato) para highlighting.
    """

    SQL_KEYWORDS = {
        "SELECT", "FROM", "WHERE", "INSERT", "UPDATE", "DELETE", "DROP",
        "CREATE", "ALTER", "TRUNCATE", "JOIN", "LEFT", "RIGHT", "INNER",
        "OUTER", "ON", "AND", "OR", "NOT", "IN", "LIKE", "BETWEEN", "IS",
        "NULL", "AS", "ORDER", "BY", "GROUP", "HAVING", "LIMIT", "OFFSET",
        "DISTINCT", "UNION", "ALL", "SET", "VALUES", "INTO", "TABLE", "INDEX",
        "VIEW", "DATABASE", "SCHEMA", "GRANT", "REVOKE", "BEGIN", "COMMIT",
        "ROLLBACK", "WITH", "CASE", "WHEN", "THEN", "ELSE", "END", "EXISTS",
        "PRIMARY", "KEY", "FOREIGN", "REFERENCES", "CONSTRAINT", "DEFAULT",
        "CHECK", "UNIQUE",
    }

    def __init__(self, document) -> None:
        """Inicializa o highlighter.

        Args:
            document: QTextDocument do QTextEdit.
        """
        super().__init__(document)
        self._keyword_format = SQLFormats.keyword_format()
        self._string_format = SQLFormats.string_format()
        self._number_format = SQLFormats.number_format()
        self._comment_format = SQLFormats.comment_format()

        # Regras de highlighting: (padrão regex, formato)
        self._rules: list = []

        # Números
        self._rules.append(
            (re.compile(r"\b\d+(\.\d+)?\b"), self._number_format)
        )

        # Comentário de linha única (--)
        self._rules.append(
            (re.compile(r"--[^\n]*"), self._comment_format)
        )

        # Comentário de bloco (/* ... */)
        self._rules.append(
            (re.compile(r"/\*.*?\*/", re.DOTALL), self._comment_format)
        )

        # Strings com aspas simples
        self._rules.append(
            (re.compile(r"'([^'\\]|\\.)*'"), self._string_format)
        )

        # Strings com aspas duplas
        self._rules.append(
            (re.compile(r'"([^"\\]|\\.)*"'), self._string_format)
        )

        # Keywords
        keyword_pattern = r"\b(" + "|".join(self.SQL_KEYWORDS) + r")\b"
        self._rules.append(
            (re.compile(keyword_pattern, re.IGNORECASE), self._keyword_format)
        )

    def highlightBlock(self, text: str) -> None:
        """Aplica highlighting ao bloco de texto.

        Args:
            text: Linha de texto a ser processada.
        """
        for pattern, fmt in self._rules:
            for match in pattern.finditer(text):
                start = match.start()
                end = match.end()
                self.setFormat(start, end - start, fmt)
