import time
from typing import Any

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QListView
from meshcore import EventType
from meshcore.events import Event

from ..models.message import Message
from ..models.message_list_model import MessageListModel


class MessageController(QObject):
    new_channel_message = Signal(int)
    new_private_message = Signal(str)

    def __init__(self, view: QListView, parent: QObject | None = None):
        super().__init__(parent)

        self.view: QListView = view
        self.current_chat: int | str | None = None
        self.channel_models: dict[int | str, MessageListModel] = {}

    def get_channel_model(self, chat: int | str) -> MessageListModel:
        if chat not in self.channel_models:
            self.channel_models[chat] = MessageListModel()
        return self.channel_models[chat]

    @Slot(object)
    def set_chat(self, payload: dict[str, Any]):
        chat_id = None
        if "channel_idx" in payload:
            chat_id = payload["channel_idx"]
        elif "public_key" in payload:
            chat_id = payload["public_key"][0:12]

        if chat_id is not None:
            self.current_chat = chat_id
            model = self.get_channel_model(chat_id)
            self.view.setModel(model)

    @Slot(dict, str)
    def send_message(self, target: dict[str, Any], text: str):
        chat_id = None
        if "channel_idx" in target:
            chat_id = target["channel_idx"]
        elif "public_key" in target:
            chat_id = target["public_key"][0:12]

        if chat_id is not None:
            model = self.get_channel_model(chat_id)
            model.add_message(
                Message({"text": text, "sender_timestamp": int(time.time())})
            )

    @Slot(object)
    def process_event(self, event: Event):
        if event.type == EventType.CHANNEL_MSG_RECV:
            payload = event.payload
            chat = payload["channel_idx"]

            model = self.get_channel_model(chat)
            model.add_message(Message(payload))

            if self.current_chat != chat:
                self.new_channel_message.emit(chat)

        elif event.type == EventType.CONTACT_MSG_RECV:
            payload = event.payload
            chat = payload["pubkey_prefix"]

            model = self.get_channel_model(chat)
            model.add_message(Message(payload))

            if self.current_chat != chat:
                self.new_private_message.emit(chat)
