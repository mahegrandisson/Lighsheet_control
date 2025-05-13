
import napari
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSlider
from PyQt5.QtCore import Qt
from galvo_control import *
from app_functions import *

pi_widgets = []

class SlidesWidget(QWidget):
    def __init__(self,galvo1_val: float, galvo2_val: float):

        super().__init__()

        layout = QVBoxLayout()
        self.north_south_slider = QSlider(Qt.Horizontal)
        self.north_south_slider.setMinimum(-1500)
        self.north_south_slider.setMaximum(1500)
        self.north_south_slider.setValue(-int(galvo2_val/0.001))
        self.north_south_slider.setTickInterval(1)
        self.north_south_slider.setTickPosition(QSlider.TicksBelow)
        self.north_south_slider.valueChanged.connect(self.move_north_south)

        self.east_west_slider = QSlider(Qt.Horizontal)
        self.east_west_slider.setMinimum(-50)
        self.east_west_slider.setMaximum(50)
        self.east_west_slider.setValue(int(galvo1_val/0.001))
        self.east_west_slider.setTickInterval(1)
        self.east_west_slider.setTickPosition(QSlider.TicksBelow)
        self.east_west_slider.valueChanged.connect(self.move_east_west)

        set_galvos_position(galvo1_val, galvo_id=1)
        set_galvos_position(galvo2_val, galvo_id=2)

        self.north_south_label = QLabel(f"SOUTH/NORTH : {galvo2_val} V")
        self.east_west_label = QLabel(f"WEST/EAST : {galvo1_val} V")

        layout.addWidget(self.north_south_label)
        layout.addWidget(self.north_south_slider)
        layout.addWidget(self.east_west_label)
        layout.addWidget(self.east_west_slider)

        self.reset_galvo_values = QPushButton(f"RESET")
        self.reset_galvo_values.clicked.connect(self.reset_galvos)
        layout.addWidget(self.reset_galvo_values)

        self.save_button = QPushButton("Save All Params")
        self.save_button.clicked.connect(self.save_all_params)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    @save_params_for_all_widgets(pi_widgets)
    def save_all_params(self, _):
        self.save_params()

    def scan_state(self, msg: int):
        if msg == 0:
            self.state_label.setText("Scan finished !")
        if msg == 1:
            self.state_label.setText("Scanning...")

    def move_north_south(self):
        """Déplacer le galvo nord-sud (axe Y)"""
        value = -self.north_south_slider.value() * 0.001
        set_galvos_position(value=value, galvo_id=2)
        self.north_south_label.setText(f"NORTH/SOUTH : {value:.3f} V")

    def move_east_west(self):
        """Déplacer le galvo est-ouest (axe X)"""
        value = self.east_west_slider.value() * 0.001
        set_galvos_position(value=value, galvo_id=1)
        self.east_west_label.setText(f"EAST/WEST : {value:.3f} V")

    def reset_galvos(self):
        set_galvos_position(0, galvo_id=1)
        set_galvos_position(0, galvo_id=2)
        self.north_south_label.setText(f"NORTH/SOUTH : {0:.3f} V")
        self.east_west_label.setText(f"EAST/WEST : {0:.3f} V")
        self.north_south_slider.setValue(0)
        self.east_west_slider.setValue(0)

    def save_params(self):

        val_NS = -self.north_south_slider.value() * 0.001
        val_EW = self.east_west_slider.value() * 0.001
        config = load_yaml(CONFIG)
        config["galvo1_val"] = val_EW
        config["galvo2_val"] = val_NS
        save_yaml(config, CONFIG)



if __name__=="__main__":
    params = load_yaml(CONFIG)
    galvo1_val = float(params["galvo1_val"])
    galvo2_val = float(params["galvo2_val"])
    app = napari.Viewer()
    widget = SlidesWidget(0,0)
    app.window.add_dock_widget(widget, area='left')
    napari.run()
