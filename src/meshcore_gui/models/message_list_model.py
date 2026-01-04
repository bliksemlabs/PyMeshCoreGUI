from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt

from .message import Message


class MessageListModel(QAbstractListModel):
    def __init__(self, messages: list[Message] | None = None):
        super().__init__()
        self._messages = messages or []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._messages)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        msg = self._messages[index.row()]

        if role == Qt.DisplayRole:
            return msg.formatted()

        if role == Qt.UserRole:
            return msg.payload

        return None

    def add_message(self, message: Message):
        self.beginInsertRows(QModelIndex(), len(self._messages), len(self._messages))
        self._messages.append(message)
        self.endInsertRows()

    def clear(self):
        self.beginResetModel()
        self._messages.clear()
        self.endResetModel()
