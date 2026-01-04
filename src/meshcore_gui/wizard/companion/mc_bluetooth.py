from PySide6.QtCore import QObject, Slot, Signal, QSettings
from PySide6.QtBluetooth import (
    QBluetoothDeviceDiscoveryAgent,
    QBluetoothDeviceInfo,
)


class BluetoothConnection(QObject):
    """
    Bluetooth connection implemented using PySide6 QtBluetooth.
    Supports asynchronous scanning with live updates, connecting via RFCOMM,
    and returning device info after successful connection.
    """

    device_discovered = Signal(QBluetoothDeviceInfo)  # signaal voor GUI live update
    scan_finished = Signal()  # signaal als scan klaar is

    def __init__(self, application_controller):
        super().__init__()
        self.application_controller = application_controller
        self.device_list = []  # opgeslagen QBluetoothDeviceInfo objecten
        self.connected_socket = None  # QBluetoothSocket
        self.device_info = None  # dict met name/public_key
        self.agent = QBluetoothDeviceDiscoveryAgent()
        self.agent.setLowEnergyDiscoveryTimeout(5000)

        # Verbind agent signalen naar interne slots
        self.agent.deviceDiscovered.connect(self._on_device_discovered)
        self.agent.finished.connect(self._on_scan_finished)

    def start_scan(self):
        self.device_list.clear()
        self.agent.start()

    @Slot(QBluetoothDeviceInfo)
    def _on_device_discovered(self, device_info: QBluetoothDeviceInfo):
        self.device_list.append(device_info)
        self.device_discovered.emit(device_info)

    @Slot()
    def _on_scan_finished(self):
        self.scan_finished.emit()

    def connect(self, device_name_or_address: str, slot) -> bool:
        print(device_name_or_address)
        settings = QSettings()
        settings.beginGroup("interface")
        settings.setValue("type", "bluetooth")
        settings.setValue("addr", device_name_or_address)
        settings.endGroup()

        if self.application_controller.attempt_connection():
            slot(self.application_controller)
