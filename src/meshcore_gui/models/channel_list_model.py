from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt
from PySide6.QtGui import QFont, QBrush, QColor

from .channel import Channel


class ChannelListModel(QAbstractListModel):
    def __init__(self, channels: list[Channel] | None = None):
        super().__init__()
        self._channels: list[Channel] = channels or []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._channels)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        channel = self._channels[index.row()]

        if role == Qt.DisplayRole:
            return channel.name

        elif role == Qt.UserRole:
            return channel.payload

        elif role == Qt.FontRole and channel.new_message > 0:
            font = QFont()
            font.setBold(True)
            return font

        elif role == Qt.ForegroundRole and channel.new_message > 0:
            return QBrush(QColor("red"))  # Mark new messages

        return None

    def add_or_update(self, channel: Channel):
        # Update existing channel by channel_idx
        for row, existing in enumerate(self._channels):
            if existing.channel_idx == channel.channel_idx:
                self._channels[row] = channel
                idx = self.index(row)
                self.dataChanged.emit(idx, idx, [Qt.DisplayRole, Qt.UserRole])
                return

        # New channel
        self.beginInsertRows(QModelIndex(), len(self._channels), len(self._channels))
        self._channels.append(channel)
        self.endInsertRows()

    def set_new_message(self, channel_idx: int, reset: bool = False):
        for row, item in enumerate(self._channels):
            if item.channel_idx == channel_idx:
                if reset:
                    item.set_new_message(0)
                else:
                    item.set_new_message(1)

                idx = self.index(row, 0)
                self.dataChanged.emit(
                    idx, idx, [Qt.DisplayRole, Qt.FontRole, Qt.ForegroundRole]
                )
                break
