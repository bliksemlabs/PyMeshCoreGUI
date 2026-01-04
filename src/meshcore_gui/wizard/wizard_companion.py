from PySide6.QtWidgets import QApplication, QWizard

from PySide6.QtCore import Signal

from .companion.connection import ConnectionTypePage
from .companion.deviceselection import DeviceSelectionPage
from .companion.devicestatus import DeviceStatusPage


# ========================
# Wizard
# ========================
class CompanionWizard(QWizard):
    completed = Signal(bool)

    def accept(self):
        self.completed.emit(True)
        super().accept()

    def reject(self):
        self.completed.emit(False)
        super().reject()

    def __init__(self, application_controller):
        super().__init__()
        self.application_controller = application_controller
        self.addPage(ConnectionTypePage())
        self.addPage(DeviceSelectionPage(self))
        self.addPage(DeviceStatusPage(self))
        self.setWindowTitle("Companion Wizard")


# ========================
# Main
# ========================
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    wizard = CompanionWizard()
    wizard.show()

    sys.exit(app.exec())
