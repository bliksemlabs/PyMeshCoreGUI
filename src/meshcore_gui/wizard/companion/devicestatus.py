from PySide6.QtWidgets import (
    QWizardPage,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)

from pathlib import Path

from .mc_bluetooth import BluetoothConnection
from .mc_serial import SerialConnection
from .community_presets import PresetSelector


class DeviceStatusPage(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.setTitle("Check device properties")
        self.wizard_ref = wizard
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.name_label = QLabel("Name")
        self.name = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name)

        self.pubkey = QLineEdit()
        self.pubkey.setEnabled(False)
        self.pubkey_label = QLabel("Public Key")
        layout.addWidget(self.pubkey_label)
        layout.addWidget(self.pubkey)

        base_path = Path(__file__).parent
        self.profile_dropdown = PresetSelector(
            base_path / "community-presets.json"
        )
        layout.addWidget(self.profile_dropdown)

        self.button_save = QPushButton("Save")
        self.button_save.setEnabled(False)
        layout.addWidget(self.button_save)

        self._initial_name = None
        self._initial_profile = None

        self.name.textChanged.connect(self._update_dirty_state)
        self.profile_dropdown.combo.currentIndexChanged.connect(
            self._update_dirty_state
        )
        self.button_save.clicked.connect(self._on_save_clicked)

    def _update_dirty_state(self) -> None:
        name_changed = self.name.text() != self._initial_name
        profile_changed = (
            self.profile_dropdown.combo.currentData() != self._initial_profile
        )
        self._is_dirty = name_changed or profile_changed
        self.button_save.setEnabled(self._is_dirty)

    def _on_save_clicked(self) -> None:
        if not self._is_dirty:
            return

        self._save_data()

    def _save_data(self) -> None:
        new_name = self.name.text()
        new_profile = self.profile_dropdown.combo.currentData()

        if new_name != self._initial_name:
            self.wizard_ref.application_controller.meshcore_controller.set_name(
                new_name
            )
            self._initial_name = new_name

        if new_profile != self._initial_profile:
            freq, bw, sf, cr = new_profile.split("-")
            self.wizard_ref.application_controller.meshcore_controller.set_radio(
                float(freq), float(bw), int(sf), int(cr)
            )
            self._initial_profile = new_profile

        self._is_dirty = False
        self.button_save.setEnabled(False)

    def validatePage(self) -> bool:
        if self._is_dirty:
            self._save_data()
        return True

    def update_profile(self, application_controller):
        self.info = self.wizard_ref.application_controller.mc.self_info
        if "name" in self.info:
            self.name.setText(self.info["name"])
            self.pubkey.setText(self.info["public_key"])
            self.profile_dropdown.select_by_self_info(self.info)

            self._initial_name = self.name.text()
            self._initial_profile = self.profile_dropdown.combo.currentData()
            self._is_dirty = False
        self.button_save.setEnabled(False)

    def initializePage(self):
        conn = self.wizard_ref.connection
        if isinstance(conn, SerialConnection):
            conn.connect(
                self.wizard_ref.page(1).device_list.currentItem().text(),
                self.update_profile,
            )
        elif isinstance(conn, BluetoothConnection):
            conn.connect(
                self.wizard_ref.page(1).device_list.currentItem().text(),
                self.update_profile,
            )
