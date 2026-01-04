from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtCore import QJsonDocument

class PresetSelector(QWidget):
    def __init__(self, json_file):
        super().__init__()
        self.setWindowTitle("Community Presets")

        # Layout
        layout = QVBoxLayout(self)

        # ComboBox
        self.combo = QComboBox()
        layout.addWidget(self.combo)

        # Load JSON and populate combobox
        self.load_presets(json_file)

    def load_presets(self, json_file):
        file = QFile(json_file)
        if not file.open(QIODevice.ReadOnly | QIODevice.Text):
            raise RuntimeError(f"Cannot open {json_file}")

        data = file.readAll()
        file.close()

        doc = QJsonDocument.fromJson(data)
        if not doc.isObject():
            raise ValueError("Invalid JSON root object")

        root = doc.object()
        presets = root.get("presets", [])

        for preset in presets:
            preset_lookup = "-".join(
                [
                    str(preset["frequency_mhz"]),
                    str(int(preset["bandwidth_khz"])),
                    str(preset["spreading_factor"]),
                    str(preset["coding_rate"]),
                ]
            )
            self.combo.addItem(preset["name"], userData=preset_lookup)

    def select_by_self_info(self, self_info: dict):
        preset_lookup = "-".join(
            [
                str(self_info["radio_freq"]),
                str(int(self_info["radio_bw"])),
                str(self_info["radio_sf"]),
                str(self_info["radio_cr"]),
            ]
        )
        index = self.combo.findData(preset_lookup)
        if index != -1:
            self.combo.setCurrentIndex(index)
        else:
            self.combo.addItem("Custom", userData=preset_lookup)
            index = self.combo.findData(preset_lookup)
            self.combo.setCurrentIndex(index)
