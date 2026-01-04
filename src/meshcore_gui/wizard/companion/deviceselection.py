from PySide6.QtWidgets import (
    QWizardPage,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QLineEdit,
)
from PySide6.QtCore import Slot

from .mc_bluetooth import BluetoothConnection
from .mc_serial import SerialConnection


class DeviceSelectionPage(QWizardPage):
    def __init__(self, wizard):
        super().__init__()
        self.setTitle("Select Device")
        self.wizard_ref = wizard
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Select Device:")
        self.layout.addWidget(self.label)

        self.device_list = QListWidget()

        self.ip_field = QLineEdit()
        self.ip_field.setPlaceholderText("Hostname / IP")
        self.port_field = QLineEdit()
        self.port_field.setPlaceholderText("Port")

    def initializePage(self):
        conn_page = self.wizard_ref.page(0)

        # Clear old widgets
        self.device_list.clear()
        self.layout.removeWidget(self.device_list)
        self.layout.removeWidget(self.ip_field)
        self.layout.removeWidget(self.port_field)

        if conn_page.bt_radio.isChecked():
            self.wizard_ref.connection = BluetoothConnection(
                self.wizard_ref.application_controller
            )
            self.label.setText("Select a Bluetooth device")
            self.layout.addWidget(self.device_list)

            agent = self.wizard_ref.connection.agent
            agent.deviceDiscovered.connect(self.add_device)
            agent.finished.connect(self.scan_finished)
            agent.start()

        elif conn_page.serial_radio.isChecked():
            self.wizard_ref.connection = SerialConnection(
                self.wizard_ref.application_controller
            )
            self.label.setText("Select a serial port")
            devices = self.wizard_ref.connection.scan_devices()
            self.device_list.addItems(devices)
            self.layout.addWidget(self.device_list)

        elif conn_page.tcp_radio.isChecked():
            self.label.setText("TCP/IP connection")
            self.layout.addWidget(self.ip_field)
            self.layout.addWidget(self.port_field)

    @Slot(object)
    def add_device(self, device_info):
        self.device_list.addItem(device_info.name())
        self.wizard_ref.connection.device_list.append(device_info)

    @Slot()
    def scan_finished(self):
        pass
