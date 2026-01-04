from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt
from PySide6.QtGui import QFont, QBrush, QColor

from .contact import Contact


class ContactListModel(QAbstractListModel):
    """Model that manages a list of contacts for a QListView"""

    def __init__(self, contacts: list[Contact] | None = None):
        super().__init__()
        self._contacts = contacts or []

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        contact = self._contacts[index.row()]

        if role == Qt.DisplayRole:
            return contact.name

        elif role == Qt.UserRole:
            return contact.payload

        elif role == Qt.FontRole and contact.new_message > 0:
            font = QFont()
            font.setBold(True)
            return font

        elif role == Qt.ForegroundRole and contact.new_message > 0:
            return QBrush(QColor("red"))

        return None

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._contacts)

    def add_contact(self, contact: Contact):
        """Add a new contact or update an existing one based on public_key"""
        for row, existing in enumerate(self._contacts):
            if existing.public_key == contact.public_key:
                self._contacts[row] = contact
                index = self.index(row)
                self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.UserRole])
                return

        # If not found, add as a new contact
        self.beginInsertRows(QModelIndex(), len(self._contacts), len(self._contacts))
        self._contacts.append(contact)
        self.endInsertRows()

    def remove_contact(self, row: int):
        """Remove contact at index"""
        if 0 <= row < len(self._contacts):
            self.beginRemoveRows(QModelIndex(), row, row)
            self._contacts.pop(row)
            self.endRemoveRows()

    def clear(self):
        """Remove all contacts"""
        self.beginResetModel()
        self._contacts.clear()
        self.endResetModel()

    def set_new_message(self, pubkey_prefix: str, reset: bool = False):
        for row, item in enumerate(self._contacts):
            if item.public_key and item.public_key.startswith(pubkey_prefix):
                if reset:
                    item.set_new_message(0)
                else:
                    item.set_new_message(1)

                idx = self.index(row, 0)
                self.dataChanged.emit(
                    idx, idx, [Qt.DisplayRole, Qt.FontRole, Qt.ForegroundRole]
                )
                break
