import napari
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
)
from app_functions import (
    load_yaml,
    save_yaml,
    CONFIG,
)
from PiController import (
    PiController,
)
import time
from SlidesWidget import (
    pi_widgets,
)


class PIControlWidget(QWidget):
    def __init__(
        self,
        pi_controller: PiController,
        pi_val: float,
        controller_id: int,
        mini: float,
        maxi: float,
    ):
        super().__init__()
        self.limit_step = 4
        self.pi_controller = pi_controller
        self.controller_id = controller_id
        axe = 1
        # Interface utilisateur
        self.setWindowTitle(f"PI Position Control - Device {controller_id}")
        layout = QVBoxLayout()
        self.max = maxi  # a regarder pour chacun
        self.min = mini  # a regarder pour chacun
        # Paramètres de position
        if controller_id == 1:
            self.title_label = QLabel(
                f"Device {controller_id} | Z stage "
                f"- < : Towards objective | > : Towards us"
            )

            self.step_label = QLabel("Step: (mm)")
            init_value = "0.1"

        elif controller_id == 2:
            self.title_label = QLabel(
                f"Device {controller_id} | Theta stage "
                f"- < : Counter clockwise | > : Clockwise"
            )

            self.step_label = QLabel("Step: (deg)")
            init_value = "1"

        elif controller_id == 3:
            self.title_label = QLabel(
                f"Device {controller_id} | X stage - < : Left | > : Right"
            )

            self.step_label = QLabel("Step: (mm)")
            init_value = "0.1"

        elif controller_id == 4:
            self.title_label = QLabel(
                f"Device {controller_id} | Y stage - < : Up | > : Down"
            )
            self.step_label = QLabel("Step: (mm)")
            init_value = "0.1"
        self.title_label.setStyleSheet(
            "color: pink;font-family: 'Arial Black';font-weight: bold;"
        )
        layout.addWidget(self.title_label)
        self.step_input = QLineEdit(init_value)
        layout.addWidget(self.step_label)
        layout.addWidget(self.step_input)
        self.pi_controller.move_abs(
            self.controller_id,
            pi_val,
        )
        while not pi_controller.devices[self.controller_id - 1].gcscommands.qONT(axe)[
            1
        ]:
            time.sleep(0.05)
        self.position_label = QLabel("Position:")
        init_value = str(
            round(
                pi_controller.get_pos(device_id=controller_id),
                3,
            )
        )
        self.position_input = QLineEdit(init_value)
        layout.addWidget(self.position_label)
        layout.addWidget(self.position_input)

        self.arrow_layout = QHBoxLayout()

        self.down_button = QPushButton("<")
        self.down_button.clicked.connect(self.move_down)
        self.arrow_layout.addWidget(self.down_button)

        self.up_button = QPushButton(">")
        self.up_button.clicked.connect(self.move_up)
        self.arrow_layout.addWidget(self.up_button)

        layout.addLayout(self.arrow_layout)

        self.send_button = QPushButton(f"Send Abs Position to Device {controller_id}")
        layout.addWidget(self.send_button)

        self.err_display = QLabel("")

        layout.addWidget(self.err_display)

        self.send_button.clicked.connect(self.send_position)

        self.setLayout(layout)

    def move_up(
        self,
    ):
        txt = self.step_input.text()
        value = float(self.position_input.text())

        try:
            steps = float(txt)
            self.err_display.setText("")
        except Exception as e:
            self.err_display.setText(f"Invalid step: {e}")
            steps = 0

        if not (self.down_button.isEnabled()):
            self.down_button.setEnabled(True)

        if value >= self.max:
            self.up_button.setDisabled(True)
            self.err_display.setText(f"Max is {self.max}")
        elif value + steps > self.max:
            self.err_display.setText(f"Max is {self.max}")
        else:

            if -self.limit_step <= steps <= self.limit_step:
                self.pi_controller.move_rel(
                    self.controller_id,
                    steps,
                )
                self.position_input.setText(
                    str(
                        round(
                            float(value + steps),
                            3,
                        )
                    )
                )
            else:
                self.err_display.setText(
                    f"step should be between {-self.limit_step} and { self.limit_step}"
                )

    def move_down(
        self,
    ):
        txt = self.step_input.text()
        try:
            steps = float(txt)
            self.err_display.setText("")
        except Exception as e:
            self.err_display.setText(f"Invalid step: {e}")
            steps = 0

        value = float(self.position_input.text())

        if not (self.up_button.isEnabled()):
            self.up_button.setEnabled(True)
        if value <= self.min:
            self.down_button.setDisabled(True)
            self.err_display.setText(f"Min is {self.min}")
        elif value - steps < self.min:
            self.err_display.setText(f"Min is {self.min}")
        else:
            if -self.limit_step <= steps <= self.limit_step:
                self.pi_controller.move_rel(
                    self.controller_id,
                    -steps,
                )
                self.position_input.setText(
                    str(
                        round(
                            value - steps,
                            3,
                        )
                    )
                )
            else:
                self.err_display.setText(
                    f"step should be between {-self.limit_step} and { self.limit_step}"
                )

    def send_position(
        self,
    ):
        position_txt = self.position_input.text()
        try:
            position = float(position_txt)
            self.err_display.setText("")
        except Exception as e:
            self.err_display.setText(f"Invalid value: {e}")
            return
        if position < self.min:
            self.err_display.setText(f"Min is {self.min}")
        elif position > self.max:
            self.err_display.setText(f"Max is {self.max}")
        else:
            self.pi_controller.move_abs(
                self.controller_id,
                position,
            )
            time.sleep(1)
            self.position_input.setText(str(position))

    def save_params(
        self,
    ):
        val = self.position_input.text()
        config = load_yaml(CONFIG)
        config[f"pi{self.controller_id}_val"] = float(val)
        save_yaml(
            config,
            CONFIG,
        )


if __name__ == "__main__":
    params = load_yaml(CONFIG)
    pi1_val = float(params["pi1_val"])
    pi2_val = float(params["pi2_val"])
    pi3_val = float(params["pi3_val"])
    pi4_val = float(params["pi4_val"])
    pi_vals = []
    pi_vals.append(pi1_val)
    pi_vals.append(pi2_val)
    pi_vals.append(pi3_val)
    pi_vals.append(pi4_val)
    app = napari.Viewer()

    pi_controller = PiController()
    for i in range(
        1,
        5,
    ):
        if i == 1:
            mini = 8
            maxi = 16.999
        elif i == 2:
            mini = -360
            maxi = 360
        elif i == 3:
            mini = 4
            maxi = 16.999
        else:
            mini = 0.001
            maxi = 16.999
        pi_widget = PIControlWidget(
            pi_controller,
            pi_vals[i - 1],
            controller_id=i,
            mini=mini,
            maxi=maxi,
        )
        app.window.add_dock_widget(
            pi_widget,
            area="right",
        )
        pi_widgets.append(pi_widget)

    napari.run()
