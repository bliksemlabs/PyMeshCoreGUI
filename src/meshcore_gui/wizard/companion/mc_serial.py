from PySide6.QtSerialPort import QSerialPortInfo
from PySide6.QtCore import QSettings


class SerialConnection:
    """
    Serial connection class using PySide6 QtSerialPort.
    Only scans available serial ports on the host system.
    """

    def __init__(self, application_controller):
        self.application_controller = application_controller
        self.device_list = []
        self.connected_port = None
        self.device_info = None

    def scan_devices(self) -> list[str]:
        """
        Scan beschikbare seriële poorten en retourneer een lijst van naamstrings.
        """
        self.device_list = QSerialPortInfo.availablePorts()
        # Return human-readable strings, bijv. "COM3 - USB Serial"
        devices = []
        for port in self.device_list:
            name = port.systemLocation()  # COM3 or /dev/ttyUSB0
            desc = port.description()  # bv. "USB Serial"
            devices.append(f"{name} - {desc}")
        return devices

    def connect(self, device_string: str, slot) -> bool:
        settings = QSettings()
        settings.beginGroup("interface")
        settings.setValue("type", "serial")
        settings.setValue("port", device_string.split(" - ")[0])  # TODO
        settings.setValue("baudrate", 115200)
        settings.endGroup()

        if self.application_controller.attempt_connection():
            slot(self.application_controller)
