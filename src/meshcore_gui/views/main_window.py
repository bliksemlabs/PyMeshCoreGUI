from typing import Any, TYPE_CHECKING

from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QListView,
    QHBoxLayout,
    QLineEdit,
)

if TYPE_CHECKING:
    from controllers.meshcore_controller import MeshCoreController


class MeshCoreWidget(QWidget):
    text_submitted = Signal(object, str)

    def __init__(self):
        super().__init__()
        self.controller: "MeshCoreController" | None = None
        self.current_target: dict[str, Any] | None = None

        # GUI layout
        self.layout = QVBoxLayout(self)
        self.label_info = QLabel("Node info: ...")
        self.button_adv = QPushButton("Adv")
        self.list_contacts = QListView()
        self.list_channels = QListView()
        self.list_msgs = QListView()

        option_layout = QHBoxLayout()
        option_layout.addWidget(self.label_info, stretch=1)
        option_layout.addWidget(self.button_adv)

        option_panel = QWidget()
        option_panel.setLayout(option_layout)
        self.layout.addWidget(option_panel)

        self.layout.addWidget(QLabel("Contacts:"))
        self.layout.addWidget(self.list_contacts)
        self.layout.addWidget(QLabel("Channels:"))
        self.layout.addWidget(self.list_channels)
        self.layout.addWidget(QLabel("Messages:"))
        self.layout.addWidget(self.list_msgs)

        # --- Input area ---
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Type a message…")
        self.send_button = QPushButton("Send")

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_line, stretch=1)
        input_layout.addWidget(self.send_button)

        input_panel = QWidget()
        input_panel.setLayout(input_layout)
        self.layout.addWidget(input_panel)

        self.send_button.clicked.connect(self._on_send_clicked)
        self.input_line.returnPressed.connect(self._on_send_clicked)

    @Slot(object)
    def set_target(self, target: dict[str, Any]):
        self.current_target = target

    def _on_send_clicked(self):
        if self.current_target is not None:
            text = self.input_line.text().strip()
            if text:
                self.text_submitted.emit(self.current_target, text)

    @Slot(object)
    def on_sent(self, event: Any):
        self.input_line.clear()

    @Slot(object)
    def update_self_info(self, info: dict[str, Any]):
        self.label_info.setText(f"Node info: {info.get('name', 'N/A')}")

    def setController(self, controller: "MeshCoreController"):
        self.controller = controller

    def closeEvent(self, event: QCloseEvent):
        if self.controller:
            # Stop streaming and executor loop
            self.controller.shutdown()

        event.accept()  # Allow the window to close
