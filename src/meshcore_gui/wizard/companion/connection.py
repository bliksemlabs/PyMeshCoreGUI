from PySide6.QtWidgets import (
    QWizardPage,
    QVBoxLayout,
    QLabel,
    QRadioButton,
    QButtonGroup,
)


# ========================
# Wizard Pages
# ========================
class ConnectionTypePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Choose connection type")
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("In which way do you wat to connect?"))

        self.serial_radio = QRadioButton("Serial")
        self.serial_radio.setChecked(True)
        self.bt_radio = QRadioButton("Bluetooth")
        self.bt_radio.setEnabled(True)
        self.tcp_radio = QRadioButton("TCP/IP")
        self.tcp_radio.setEnabled(False)
        layout.addWidget(self.serial_radio)
        layout.addWidget(self.bt_radio)
        layout.addWidget(self.tcp_radio)

        self.group = QButtonGroup()
        self.group.addButton(self.serial_radio)
        self.group.addButton(self.bt_radio)
        self.group.addButton(self.tcp_radio)

    def validatePage(self) -> bool:
        return (
            self.bt_radio.isChecked()
            or self.serial_radio.isChecked()
            or self.tcp_radio.isChecked()
        )
