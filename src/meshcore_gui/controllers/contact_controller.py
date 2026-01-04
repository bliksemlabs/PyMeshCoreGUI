from PySide6.QtCore import QObject, Slot, Signal, Qt, QItemSelection
from PySide6.QtWidgets import QListView
from meshcore import EventType
from meshcore.events import Event

from ..models.contact import Contact
from ..models.contact_list_model import ContactListModel


class ContactController(QObject):
    selected = Signal(object)

    def __init__(self, view: QListView, parent: QObject | None = None):
        super().__init__(parent)

        self.view = view
        self.model = ContactListModel()
        self.view.setModel(self.model)
        self.view.setSelectionMode(QListView.SingleSelection)
        selection_model = self.view.selectionModel()
        selection_model.selectionChanged.connect(self._on_selected)

    def _on_selected(self, selected: QItemSelection, deselected: QItemSelection):
        if not selected.indexes():
            return

        index = selected.indexes()[0]
        data = index.data(Qt.UserRole)
        if data and "public_key" in data:
            self.model.set_new_message(data["public_key"], True)
            self.selected.emit(data)

    @Slot(str)
    def new_private_message(self, pubkey_prefix: str):
        self.model.set_new_message(pubkey_prefix, False)

    @Slot()
    def deselect(self):
        if self.view.selectionModel().hasSelection():
            self.view.selectionModel().clearSelection()

    @Slot(object)
    def process_event(self, event: Event):
        if event.type == EventType.CONTACTS:
            for contact_payload in event.payload.values():
                contact = Contact(contact_payload)
                self.model.add_contact(contact)

        elif (
            event.type == EventType.NEW_CONTACT or event.type == EventType.NEXT_CONTACT
        ):
            contact = Contact(event.payload)
            self.model.add_contact(contact)
