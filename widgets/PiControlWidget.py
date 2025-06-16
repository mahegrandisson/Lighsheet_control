import napari
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
)
from app_func.app_functions import load_yaml, save_yaml, CONFIG
from pi_contol.PiController import PiController
import time
from widgets.GalvoWidget import pi_widgets


class PIControlWidget(QWidget):
    def __init__(self, pi_controller: PiController, pi_val: float, controller_id: int, mini: float, maxi: float):
        super().__init__()

        self.limit_step = 4  # Maximum allowed step size for move commands
        self.pi_controller = pi_controller
        self.controller_id = controller_id
        self.min = mini
        self.max = maxi
        axe = 1  # Axis, presumably fixed here

        # Set window title
        self.setWindowTitle(f"PI Position Control - Device {controller_id}")

        layout = QVBoxLayout()

        # Title and step label according to device id
        if controller_id == 1:
            self.title_label = QLabel(
                f"Device {controller_id} | Z stage - < : Towards objective | > : Towards us"
            )
            self.step_label = QLabel("Step: (mm)")
            init_step_value = "0.1"
        elif controller_id == 2:
            self.title_label = QLabel(
                f"Device {controller_id} | Theta stage - < : Counter clockwise | > : Clockwise"
            )
            self.step_label = QLabel("Step: (deg)")
            init_step_value = "1"
        elif controller_id == 3:
            self.title_label = QLabel(
                f"Device {controller_id} | X stage - < : Left | > : Right"
            )
            self.step_label = QLabel("Step: (mm)")
            init_step_value = "0.1"
        else:
            self.title_label = QLabel(
                f"Device {controller_id} | Y stage - < : Up | > : Down"
            )
            self.step_label = QLabel("Step: (mm)")
            init_step_value = "0.1"

        self.title_label.setStyleSheet("color: white; font-family: 'Arial Black'; font-weight: bold;")
        layout.addWidget(self.title_label)

        self.step_input = QLineEdit(init_step_value)
        layout.addWidget(self.step_label)
        layout.addWidget(self.step_input)

        # Move device to initial position
        self.pi_controller.move_abs(self.controller_id, pi_val)
        # Wait until motion is complete
        while not pi_controller.devices[self.controller_id - 1].gcscommands.qONT(axe)[1]:
            time.sleep(0.05)

        # Position label and input
        self.position_label = QLabel("Position:")
        current_pos = round(pi_controller.get_pos(device_id=controller_id), 3)
        self.position_input = QLineEdit(str(current_pos))
        layout.addWidget(self.position_label)
        layout.addWidget(self.position_input)

        # Buttons layout for moving position relative to step size
        self.arrow_layout = QHBoxLayout()

        self.down_button = QPushButton("<")
        self.down_button.clicked.connect(self.move_down)
        self.arrow_layout.addWidget(self.down_button)

        self.up_button = QPushButton(">")
        self.up_button.clicked.connect(self.move_up)
        self.arrow_layout.addWidget(self.up_button)

        layout.addLayout(self.arrow_layout)

        # Button to send absolute position to device
        self.send_button = QPushButton(f"Send Abs Position to Device {controller_id}")
        self.send_button.clicked.connect(self.send_position)
        layout.addWidget(self.send_button)

        # Label to display errors
        self.err_display = QLabel("")
        layout.addWidget(self.err_display)

        self.setLayout(layout)

    def move_up(self):
        try:
            steps = float(self.step_input.text())
            self.err_display.setText("")
        except Exception as e:
            self.err_display.setText(f"Invalid step: {e}")
            return

        try:
            value = float(self.position_input.text())
        except Exception as e:
            self.err_display.setText(f"Invalid position: {e}")
            return

        if value >= self.max:
            self.up_button.setDisabled(True)
            self.err_display.setText(f"Max is {self.max}")
            return
        elif value + steps > self.max:
            self.err_display.setText(f"Max is {self.max}")
            return
        else:
            self.up_button.setEnabled(True)
            self.down_button.setEnabled(True)

            if -self.limit_step <= steps <= self.limit_step:
                self.pi_controller.move_rel(self.controller_id, steps)
                new_val = round(value + steps, 3)
                self.position_input.setText(str(new_val))
            else:
                self.err_display.setText(f"Step should be between {-self.limit_step} and {self.limit_step}")

    def move_down(self):
        try:
            steps = float(self.step_input.text())
            self.err_display.setText("")
        except Exception as e:
            self.err_display.setText(f"Invalid step: {e}")
            return

        try:
            value = float(self.position_input.text())
        except Exception as e:
            self.err_display.setText(f"Invalid position: {e}")
            return

        if value <= self.min:
            self.down_button.setDisabled(True)
            self.err_display.setText(f"Min is {self.min}")
            return
        elif value - steps < self.min:
            self.err_display.setText(f"Min is {self.min}")
            return
        else:
            self.up_button.setEnabled(True)
            self.down_button.setEnabled(True)

            if -self.limit_step <= steps <= self.limit_step:
                self.pi_controller.move_rel(self.controller_id, -steps)
                new_val = round(value - steps, 3)
                self.position_input.setText(str(new_val))
            else:
                self.err_display.setText(f"Step should be between {-self.limit_step} and {self.limit_step}")

    def send_position(self):
        try:
            position = float(self.position_input.text())
            self.err_display.setText("")
        except Exception as e:
            self.err_display.setText(f"Invalid value: {e}")
            return

        if position < self.min:
            self.err_display.setText(f"Min is {self.min}")
        elif position > self.max:
            self.err_display.setText(f"Max is {self.max}")
        else:
            self.pi_controller.move_abs(self.controller_id, position)
            time.sleep(1)
            self.position_input.setText(str(position))

    def save_params(self):
        try:
            val = float(self.position_input.text())
            config = load_yaml(CONFIG)
            config[f"pi{self.controller_id}_val"] = val
            save_yaml(config, CONFIG)
        except Exception as e:
            self.err_display.setText(f"Error saving params: {e}")


if __name__ == "__main__":
    params = load_yaml(CONFIG)

    pi_vals = [float(params[f"pi{i}_val"]) for i in range(1, 5)]

    app = napari.Viewer()
    pi_controller = PiController()

    for i in range(1, 5):
        if i == 1:
            mini, maxi = 8, 16.999
        elif i == 2:
            mini, maxi = -360, 360
        elif i == 3:
            mini, maxi = 4, 16.999
        else:
            mini, maxi = 0.001, 16.999

        pi_widget = PIControlWidget(pi_controller, pi_vals[i - 1], controller_id=i, mini=mini, maxi=maxi)
        app.window.add_dock_widget(pi_widget, area="right")
        pi_widgets.append(pi_widget)

    napari.run()
