"""Modelo e widget para exibir resultados de queries em QTableView.

Implementa PandasModel (QAbstractTableModel) para integrar
DataFrames pandas com QTableView, incluindo sorting.
"""

import logging
from typing import Optional, Any

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtWidgets import QTableView, QSizePolicy
from PyQt5.QtGui import QColor

logger = logging.getLogger(__name__)


class PandasModel(QAbstractTableModel):
    """Modelo de tabela Qt para exibir DataFrames pandas.

    Suporta sorting por coluna, exibição de headers e contagem de linhas.

    Attributes:
        _data: DataFrame pandas a ser exibido.
    """

    def __init__(self, data=None, parent=None) -> None:
        """Inicializa o modelo com um DataFrame.

        Args:
            data: DataFrame pandas. Se None, modelo vazio.
            parent: Objeto pai Qt.
        """
        super().__init__(parent)
        self._data = data
        self._sort_column = -1
        self._sort_order = Qt.AscendingOrder

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Retorna o número de linhas.

        Args:
            parent: Índice pai (ignorado para tabelas planas).

        Returns:
            Número de linhas no DataFrame.
        """
        if self._data is None:
            return 0
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Retorna o número de colunas.

        Args:
            parent: Índice pai (ignorado).

        Returns:
            Número de colunas no DataFrame.
        """
        if self._data is None:
            return 0
        return len(self._data.columns)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Retorna o dado para o índice e role especificados.

        Args:
            index: Índice do modelo.
            role: Role do Qt (DisplayRole, BackgroundRole, etc.).

        Returns:
            Valor da célula ou QVariant inválido.
        """
        if not index.isValid():
            return QVariant()

        if self._data is None:
            return QVariant()

        row = index.row()
        col = index.column()

        if row >= len(self._data) or col >= len(self._data.columns):
            return QVariant()

        if role == Qt.DisplayRole:
            value = self._data.iloc[row, col]
            if value is None:
                return "NULL"
            # Formata floats com 4 casas decimais
            if isinstance(value, float):
                if value == int(value):
                    return str(int(value))
                return f"{value:.4f}"
            return str(value)

        if role == Qt.BackgroundRole:
            # Linhas alternadas com cor leve
            if row % 2 == 1:
                return QColor(240, 240, 240)
            return QColor(255, 255, 255)

        if role == Qt.TextAlignmentRole:
            return Qt.AlignLeft | Qt.AlignVCenter

        return QVariant()

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ) -> Any:
        """Retorna o header para a seção especificada.

        Args:
            section: Índice da coluna ou linha.
            orientation: Orientação (horizontal/vertical).
            role: Role do Qt.

        Returns:
            Texto do header ou QVariant inválido.
        """
        if role != Qt.DisplayRole:
            return QVariant()

        if self._data is None:
            return QVariant()

        if orientation == Qt.Horizontal:
            if section < len(self._data.columns):
                return str(self._data.columns[section])
            return QVariant()

        if orientation == Qt.Vertical:
            return str(section + 1)

        return QVariant()

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Retorna os flags do item (read-only).

        Args:
            index: Índice do modelo.

        Returns:
            Flags do item.
        """
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def sort(self, column: int, order: Qt.SortOrder = Qt.AscendingOrder) -> None:
        """Ordena o modelo pela coluna especificada.

        Args:
            column: Índice da coluna para ordenação.
            order: Ordem de classificação (ascendente/descendente).
        """
        if self._data is None or column >= len(self._data.columns):
            return

        self.layoutAboutToBeChanged.emit()
        col_name = self._data.columns[column]
        ascending = order == Qt.AscendingOrder
        self._data = self._data.sort_values(
            by=col_name, ascending=ascending, na_position="last"
        ).reset_index(drop=True)
        self.layoutChanged.emit()


def create_results_table(parent: Optional[Any] = None) -> QTableView:
    """Cria um QTableView configurado para exibir resultados de queries.

    Args:
        parent: Widget pai.

    Returns:
        QTableView configurado com sorting e sizing apropriado.
    """
    table = QTableView(parent)
    table.setSortingEnabled(True)
    table.setSelectionBehavior(QTableView.SelectRows)
    table.setSelectionMode(QTableView.SingleSelection)
    table.setAlternatingRowColors(True)
    table.horizontalHeader().setStretchLastSection(True)
    table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    table.setWordWrap(False)
    return table
