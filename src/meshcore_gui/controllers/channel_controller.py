from PySide6.QtCore import QObject, Slot, Signal, Qt, QItemSelection
from PySide6.QtWidgets import QListView
from meshcore import EventType
from meshcore.events import Event

from ..models.channel import Channel
from ..models.channel_list_model import ChannelListModel


class ChannelController(QObject):
    selected = Signal(object)

    def __init__(self, view: QListView, parent: QObject | None = None):
        super().__init__(parent)
        self.view = view
        self.model = ChannelListModel()
        self.view.setModel(self.model)
        self.view.setSelectionMode(QListView.SingleSelection)
        selection_model = self.view.selectionModel()
        selection_model.selectionChanged.connect(self._on_selected)

    def _on_selected(self, selected: QItemSelection, deselected: QItemSelection):
        if not selected.indexes():
            return

        index = selected.indexes()[0]
        data = index.data(Qt.UserRole)
        if data and "channel_idx" in data:
            self.model.set_new_message(data["channel_idx"], True)
            self.selected.emit(data)

    @Slot(int)
    def new_channel_message(self, channel_idx: int):
        self.model.set_new_message(channel_idx, False)

    @Slot()
    def deselect(self):
        if self.view.selectionModel().hasSelection():
            self.view.selectionModel().clearSelection()

    @Slot(object)
    def process_event(self, event: Event):
        if event.type == EventType.CHANNEL_INFO:
            channel = Channel(event.payload)

            if not channel.is_valid():
                return  # Ignore invalid channel

            self.model.add_or_update(channel)
