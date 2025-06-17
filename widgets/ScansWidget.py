import yaml
from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QFormLayout,
    QGridLayout,
    QFileDialog,
    QHBoxLayout,
    QComboBox,
)
from PyQt5.QtCore import Qt
import napari

from pymmcore_plus import (
    CMMCorePlus,
)
from pi_contol.PiController import (
    PiController,
)
from app_func.pi_ni_scan import brillouin_scan, scan
from app_func.app_functions import B_PARAMS, F_PARAMS


class ScanBTNWidget(QWidget):
    """
    Widget that contains a button to toggle the scan parameters widget.
    """

    def __init__(self, pi_controller, core):
        super().__init__()
        self.brillouin_widget = ScanWidget(pi_controller, core)

        self.setStyleSheet("background-color: rgb(38,41,48);")
        self.setWindowTitle("Scan Widget")
        self.setGeometry(100, 100, 200, 100)

        self.scan_button = QPushButton("Sync Scan parameters", self)
        self.scan_button.setStyleSheet(
            """
            background-color: rgb(180, 180, 180);
            color: black;
            font-size: 14px;
            padding: 5px;
            border-radius: 5px;
            """
        )
        self.scan_button.clicked.connect(
            lambda: self.toggle_widget(self.brillouin_widget)
        )

        layout = QVBoxLayout()
        layout.addWidget(self.scan_button, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def toggle_widget(self, widget):
        """
        Show or hide the given widget based on its current visibility state.
        """
        if not widget.hidden:
            widget.hide()
            widget.hidden = True
        else:
            widget.move(self.x() + self.width(), self.y() + 50)
            widget.show()
            widget.hidden = False


class FastScanBTNWidget(QWidget):
    def __init__(
        self,
        pi_controller,
        core,
    ):
        super().__init__()
        self.fast_scan_widget = FastScanWidget(
            pi_controller,
            core,
        )
        self.setStyleSheet("background-color: rgb(38,41,48);")
        self.setWindowTitle("Scan Widget")
        self.setGeometry(
            100,
            100,
            200,
            100,
        )
        self.scan_button = QPushButton(
            "Fast scan parameters",
            self,
        )
        self.scan_button.setStyleSheet(
            """
            background-color: rgb(180, 180, 180);
            color: black;
            font-size: 14px;
            padding: 5px;
            border-radius: 5px;
        """
        )
        self.scan_button.clicked.connect(
            lambda: self.toggle_widget(self.fast_scan_widget)
        )
        layout = QVBoxLayout()
        layout.addWidget(
            self.scan_button,
            alignment=Qt.AlignCenter,
        )

        self.setLayout(layout)

    def toggle_widget(
        self,
        widget,
    ):

        if not widget.hidden:
            widget.hide()
            widget.hidden = True
        else:

            widget.move(
                self.x() + self.width(),
                self.y() + 50,
            )
            widget.show()
            widget.hidden = False


class ScanWidget(QWidget):
    """
    Widget to set scan parameters, save/load them, and run the scan.
    """

    def __init__(self, pi_controller: PiController, core: CMMCorePlus):
        super().__init__()

        self.hidden = True
        self.pi_controller = pi_controller
        self.core = core

        # Detect connected cameras
        self.cameras = []
        self.cam_names = ["ORCA", "CAM"]
        for dev in self.core.getLoadedDevices():
            for name in self.cam_names:
                if name in dev.upper():
                    self.cameras.append(dev)

        # Path to save parameters file
        self.filepath = B_PARAMS
        self.full_path = ""

        # Default values for the scan cube corners (safe initial values)
        self.start_z, self.end_z = 16.99, 16.99
        self.start_x, self.end_x = 8, 8
        self.start_y, self.end_y = 14, 14

        # Configure widget appearance
        self.setWindowTitle("Sync Scan parameters")
        self.setGeometry(0, 0, 800, 500)
        self.setStyleSheet(
            """
            QWidget {
                background-color: rgb(38,41,48);
                color: white;
            }
            QLineEdit {
                background-color: rgb(38,41,48);
                color: white;
                border: 1px solid #666;
                padding: 4px;
            }
            QLabel {
                color: white;
            }
            """
        )
        self.setWindowFlags(Qt.Window)

        self.title_label = QLabel("Sync Scan Parameters", self)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)

        # Create input fields for cube corners and steps
        form_layout = QFormLayout()

        self.camera_input = QComboBox()
        self.camera_input.addItems(self.cameras)
        self.camera_input.setCurrentText(self.core.getCameraDevice())

        self.br_x_input = QLineEdit()
        self.br_y_input = QLineEdit()
        self.br_z_input = QLineEdit()

        self.ul_x_input = QLineEdit()
        self.ul_y_input = QLineEdit()
        self.ul_z_input = QLineEdit()

        self.x_step_input = QLineEdit()
        self.y_step_input = QLineEdit()
        self.z_step_input = QLineEdit()
        self.exposure_input = QLineEdit()

        # Info labels with valid ranges
        self.info_label = QLabel("4<=X<17 mm   |   0<Y<17 mm   |   8<=Z<17 mm")
        self.info_label.setStyleSheet(
            "color: pink;font-family: 'Arial Black';font-weight: bold;"
        )

        self.info_label_2 = QLabel("1µm <=step< 1000µm")
        self.info_label_2.setStyleSheet(
            "color: pink;font-family: 'Arial Black';font-weight: bold;"
        )

        # Grid layout for coordinate inputs
        grid_layout = QGridLayout()

        grid_layout.addWidget(QLabel("Bottom Right Cube Corner:"), 0, 0)
        grid_layout.addWidget(QLabel("X (mm):"), 0, 1)
        grid_layout.addWidget(self.br_x_input, 0, 2)
        grid_layout.addWidget(QLabel("Y (mm):"), 0, 3)
        grid_layout.addWidget(self.br_y_input, 0, 4)
        grid_layout.addWidget(QLabel("Z (mm):"), 0, 5)
        grid_layout.addWidget(self.br_z_input, 0, 6)

        grid_layout.addWidget(QLabel("Upper Left Cube Corner:"), 1, 0)
        grid_layout.addWidget(QLabel("X (mm):"), 1, 1)
        grid_layout.addWidget(self.ul_x_input, 1, 2)
        grid_layout.addWidget(QLabel("Y (mm):"), 1, 3)
        grid_layout.addWidget(self.ul_y_input, 1, 4)
        grid_layout.addWidget(QLabel("Z (mm):"), 1, 5)
        grid_layout.addWidget(self.ul_z_input, 1, 6)

        # Add step sizes, camera and exposure inputs
        form_layout.addRow("X Step (µm):", self.x_step_input)
        form_layout.addRow("Y Step (µm):", self.y_step_input)
        form_layout.addRow("Z Step (µm):", self.z_step_input)
        form_layout.addRow("camera:", self.camera_input)
        form_layout.addRow("exposure (ms):", self.exposure_input)

        # Buttons for saving parameters and running scan
        self.save_btn = QPushButton("Save Parameters")
        self.save_btn.setStyleSheet(
            """
            background-color: rgb(180, 180, 180);
            color: black;
            font-size: 14px;
            padding: 5px;
            border-radius: 5px;
            """
        )
        self.save_btn.clicked.connect(self.save_parameters)

        self.run_btn = QPushButton("Run scan")
        self.run_btn.clicked.connect(self.run_scan)

        self.disp_label = QLabel("")

        # Folder selection widgets
        self.folder_label = QLabel("Select Parent Folder")
        self.path_input = QLineEdit()
        self.folder_prefix_label = QLabel("saving folder")
        self.folder_prefix_input = QLineEdit()
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setFixedWidth(80)
        self.browse_btn.clicked.connect(self.select_folder)

        # Horizontal layout for folder selection
        layout = QHBoxLayout()
        layout.addWidget(self.folder_label)
        layout.addWidget(self.path_input)
        layout.addWidget(self.browse_btn)
        layout.addWidget(self.folder_prefix_label)
        layout.addWidget(self.folder_prefix_input)
        layout.setContentsMargins(0, 0, 0, 0)

        # Compose main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.info_label)
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.info_label_2)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(layout)
        main_layout.addWidget(self.save_btn)
        main_layout.addWidget(self.run_btn)
        main_layout.addWidget(self.disp_label)
        self.setLayout(main_layout)

        # Load parameters from file if available
        self.load_parameters()

    def save_parameters(self):
        """
        Save scan parameters to a YAML file after validation.
        """
        try:
            btc_x = float(self.br_x_input.text())
            btc_y = float(self.br_y_input.text())
            btc_z = float(self.br_z_input.text())

            ulc_x = float(self.ul_x_input.text())
            ulc_y = float(self.ul_y_input.text())
            ulc_z = float(self.ul_z_input.text())

            s_x = float(self.x_step_input.text())
            s_y = float(self.y_step_input.text())
            s_z = float(self.z_step_input.text())

            # Validate coordinate ranges
            if (
                4 <= btc_x < 17
                and 0 < btc_y < 17
                and 8 <= btc_z < 17
                and 4 <= ulc_x < 17
                and 0 < ulc_y < 17
                and 8 <= ulc_z < 17
            ):

                params = {
                    "bottom_right_corner": {"x": btc_x, "y": btc_y, "z": btc_z},
                    "upper_left_corner": {"x": ulc_x, "y": ulc_y, "z": ulc_z},
                    "steps": {"x_step": s_x, "y_step": s_y, "z_step": s_z},
                    "folder": self.path_input.text(),
                    "folder prefix": self.folder_prefix_input.text(),
                    "exposure": float(self.exposure_input.text()),
                    "camera": self.camera_input.currentText(),
                }

                with open(self.filepath, "w") as file:
                    yaml.dump(params, file, default_flow_style=False)

                self.disp_label.setText("Parameters saved!")
            else:
                self.disp_label.setText("Wrong parameter values")

        except ValueError:
            self.disp_label.setText("Parameters must be float")

    def load_parameters(self):
        """
        Load scan parameters from the YAML file and populate the input fields.
        """
        if not os.path.exists(self.filepath):
            return

        try:
            with open(self.filepath, "r") as file:
                params = yaml.safe_load(file)

            self.br_x_input.setText(str(params["bottom_right_corner"]["x"]))
            self.br_y_input.setText(str(params["bottom_right_corner"]["y"]))
            self.br_z_input.setText(str(params["bottom_right_corner"]["z"]))

            self.ul_x_input.setText(str(params["upper_left_corner"]["x"]))
            self.ul_y_input.setText(str(params["upper_left_corner"]["y"]))
            self.ul_z_input.setText(str(params["upper_left_corner"]["z"]))

            self.x_step_input.setText(str(params["steps"]["x_step"]))
            self.y_step_input.setText(str(params["steps"]["y_step"]))
            self.z_step_input.setText(str(params["steps"]["z_step"]))

            self.path_input.setText(params["folder"])
            self.folder_prefix_input.setText(params["folder prefix"])

            if params["camera"]:
                self.camera_input.setCurrentText(params["camera"])
            else:
                self.camera_input.setCurrentText(self.cameras[0])

            self.exposure_input.setText(str(params["exposure"]))

            self.disp_label.setText("Parameters loaded.")

        except Exception as e:
            self.disp_label.setText(f"Failed to load parameters: {e}")

    def run_scan(self):
        """
        Start the scan process using the entered parameters.
        """
        try:
            self.core.setExposure(float(self.exposure_input.text()))

            btc_x = float(self.br_x_input.text())
            btc_y = float(self.br_y_input.text())
            btc_z = float(self.br_z_input.text())

            ulc_x = float(self.ul_x_input.text())
            ulc_y = float(self.ul_y_input.text())
            ulc_z = float(self.ul_z_input.text())

            s_x = float(self.x_step_input.text())
            s_y = float(self.y_step_input.text())
            s_z = float(self.z_step_input.text())

            if self.camera_input:
                cam = self.camera_input.currentText()
                self.core.setCameraDevice(cam)
            else:
                self.core.setCameraDevice(self.cameras[0])

            self.disp_label.setText("Running and computing...")

            self.full_path = os.path.join(
                self.path_input.text(), self.folder_prefix_input.text()
            )

            worker = brillouin_scan(
                self.pi_controller,
                self.core,
                btc_x,
                btc_y,
                btc_z,
                ulc_x,
                ulc_y,
                ulc_z,
                s_x,
                s_y,
                s_z,
                self.full_path,
            )
            worker.start()
            worker.signals.finished.connect(lambda: self.scan_state(0))

        except Exception as e:
            self.disp_label.setText(f"Invalid parameters: {e}")
            print(self.pi_controller)

    def scan_state(self, state: int):
        """
        Update the display label after scan finishes.
        """
        if state == 0:
            self.disp_label.setText(f"Scan done! Images saved at {self.full_path}")

    def select_folder(self):
        """
        Open a folder dialog to select the parent folder for saving.
        """
        folder = QFileDialog.getExistingDirectory(self, "Select parent Folder")
        if folder:
            self.path_input.setText(folder)
        self.show()


class FastScanWidget(QWidget):
    def __init__(
        self,
        pi_controller: PiController,
        core: CMMCorePlus,
    ):
        super().__init__()
        self.hidden = True
        self.pi_controller = pi_controller
        self.core = core
        self.core.setCameraDevice(self.core.getLoadedDevices()[0])
        self.filepath = F_PARAMS
        self.full_path = ""
        # safety measure
        self.start_X = 8
        self.stop_X = 8
        self.start_Y = 8
        self.stop_Y = 8
        self.start_Z = 8
        self.stop_Z = 8

        self.setWindowTitle("Fast Scan parameters")
        self.setGeometry(
            0,
            0,
            800,
            500,
        )
        self.setStyleSheet(
            """
                    QWidget {
                        background-color: rgb(38,41,48);
                        color: white;
                    }
                    QLineEdit {
                        background-color: background-color: rgb(38,41,48);
                        color: white;
                        border: 1px solid #666;
                        padding: 4px;
                    }
                    QLabel {
                        color: white;
                    }
                """
        )
        self.setWindowFlags(Qt.Window)

        self.title_label = QLabel(
            "Fast Scan Parameters",
            self,
        )
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)

        form_layout = QFormLayout()

        self.start = QLineEdit()
        self.stop = QLineEdit()
        self.x_step_input = QLineEdit()
        self.y_step_input = QLineEdit()
        self.z_step_input = QLineEdit()
        self.freq_input = QLineEdit()

        self.info_label = QLabel()
        self.info_label.setText("4<=X<17 mm   |   0<Y<17 mm   |   8<=Z<17 mm")
        self.info_label.setStyleSheet(
            "color: pink;font-family: 'Arial Black';font-weight: bold;"
        )

        grid_layout = QGridLayout()

        grid_layout.addWidget(
            QLabel("start scan values:"),
            0,
            0,
        )
        grid_layout.addWidget(
            QLabel("X start (mm):"),
            0,
            1,
        )
        self.br_x_input = QLineEdit()
        grid_layout.addWidget(
            self.br_x_input,
            0,
            2,
        )
        grid_layout.addWidget(
            QLabel("Y start (mm):"),
            0,
            3,
        )

        self.br_y_input = QLineEdit()
        grid_layout.addWidget(
            self.br_y_input,
            0,
            4,
        )

        grid_layout.addWidget(
            QLabel("Z start (mm):"),
            0,
            5,
        )

        self.br_z_input = QLineEdit()
        grid_layout.addWidget(
            self.br_z_input,
            0,
            6,
        )

        grid_layout.addWidget(
            QLabel("end scan values:"),
            1,
            0,
        )

        grid_layout.addWidget(
            QLabel("X stop (mm):"),
            1,
            1,
        )

        self.ul_x_input = QLineEdit()
        grid_layout.addWidget(
            self.ul_x_input,
            1,
            2,
        )

        grid_layout.addWidget(
            QLabel("Y stop (mm):"),
            1,
            3,
        )
        self.ul_y_input = QLineEdit()
        grid_layout.addWidget(
            self.ul_y_input,
            1,
            4,
        )
        grid_layout.addWidget(
            QLabel("Z stop (mm):"),
            1,
            5,
        )
        self.ul_z_input = QLineEdit()
        grid_layout.addWidget(
            self.ul_z_input,
            1,
            6,
        )

        form_layout.addRow(
            "plane number (Z axis):",
            self.z_step_input,
        )
        self.duration_input = QLineEdit()
        form_layout.addRow(
            "duration:",
            self.duration_input,
        )
        form_layout.addRow(
            "frequency (Hz):",
            self.freq_input,
        )

        self.save_btn = QPushButton()
        self.save_btn.setText("Save Parameters")
        self.save_btn.setStyleSheet(
            """
            background-color: rgb(180, 180, 180);
            color: black;
            font-size: 14px;
            padding: 5px;
            border-radius: 5px;
        """
        )
        self.save_btn.clicked.connect(lambda: self.save_parameters())

        self.disp_label = QLabel()
        self.disp_label.setText("")

        self.run_btn = QPushButton()
        self.run_btn.setText("Run scan")
        self.run_btn.clicked.connect(lambda: self.run_scan())

        self.info_label_2 = QLabel()
        self.info_label_2.setText("1µm <=step< 1000µm")
        self.info_label_2.setStyleSheet(
            "color: pink;font-family: 'Arial Black';font-weight: bold;"
        )

        self.folder_label = QLabel("Select Parent Folder")
        self.path_input = QLineEdit()
        self.folder_prefix_label = QLabel("saving folder")
        self.folder_prefix_input = QLineEdit()
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setFixedWidth(80)

        # connect to browse
        self.browse_btn.clicked.connect(self.select_folder)

        # horizontal layout
        layout = QHBoxLayout()
        layout.addWidget(self.folder_label)
        layout.addWidget(self.path_input)
        layout.addWidget(self.browse_btn)
        layout.addWidget(self.folder_prefix_label)
        layout.addWidget(self.folder_prefix_input)
        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.info_label)
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.info_label_2)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(layout)
        main_layout.addWidget(self.save_btn)
        main_layout.addWidget(self.run_btn)
        main_layout.addWidget(self.disp_label)
        self.setLayout(main_layout)

        self.load_parameters()

    def run_scan(
        self,
    ):
        try:
            self.core.setExposure(float(self.freq_input.text()))
            # if self.disp_label.text() == "Parameters saved !":

            btc_y = float(self.br_y_input.text())
            btc_z = float(self.br_z_input.text())

            ulc_y = float(self.ul_y_input.text())
            ulc_z = float(self.ul_z_input.text())

            z_step = float(self.z_step_input.text())
            z_step = int(z_step)
            freq = float(self.freq_input.text())
            freq = int(freq)

            dur = float(self.duration_input.text())

            self.disp_label.setText("running and computing...")
            self.full_path = (
                self.path_input.text() + "/" + self.folder_prefix_input.text()
            )
            if not os.path.isdir(self.full_path):
                os.makedirs(self.full_path)
            worker = scan(
                self.pi_controller,
                self.core,
                1,
                btc_z,
                ulc_z,
                btc_y,
                ulc_y,
                z_step,
                freq,
                10000,
                path=self.full_path,
                duration=dur,
            )
            worker.start()
            worker.signals.finished.connect(lambda: self.scan_state(0))

            # else:
            #    self.disp_label.setText("Please save parameters first")
        except Exception as e:
            self.disp_label.setText(f"Invalid parameters:{e}")

    def scan_state(
        self,
        state: int,
    ):
        if state == 0:
            self.disp_label.setText("Scan done ! images saved at " + self.full_path)

    def select_folder(
        self,
    ):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select parent Folder",
        )
        if folder:
            self.path_input.setText(folder)
        self.show()

    def load_parameters(
        self,
    ):
        if not os.path.exists(self.filepath):
            return

        try:
            with open(
                self.filepath,
                "r",
            ) as file:
                params = yaml.safe_load(file)

            self.br_x_input.setText(str(params["bottom_right_corner"]["x"]))
            self.br_y_input.setText(str(params["bottom_right_corner"]["y"]))
            self.br_z_input.setText(str(params["bottom_right_corner"]["z"]))

            self.ul_x_input.setText(str(params["upper_left_corner"]["x"]))
            self.ul_y_input.setText(str(params["upper_left_corner"]["y"]))
            self.ul_z_input.setText(str(params["upper_left_corner"]["z"]))

            self.duration_input.setText(str(params["duration"]))
            self.z_step_input.setText(str(params["steps"]["z_step"]))

            self.path_input.setText(params["folder"])

            self.folder_prefix_input.setText(params["folder prefix"])

            self.freq_input.setText(str(params["freq"]))

            self.disp_label.setText("Parameters loaded.")

        except Exception as e:
            self.disp_label.setText(f"Failed to load parameters: {e}")

    def save_parameters(
        self,
    ):

        try:

            btc_x = float(self.br_x_input.text())
            btc_y = float(self.br_y_input.text())
            btc_z = float(self.br_z_input.text())

            ulc_x = float(self.ul_x_input.text())
            ulc_y = float(self.ul_y_input.text())
            ulc_z = float(self.ul_z_input.text())

            d = float(self.duration_input.text())
            z_step = float(self.z_step_input.text())

            if (
                4 <= btc_x < 17
                and 0 < btc_y < 17
                and 8 <= btc_z < 17
                and 4 <= ulc_x < 17
                and 0 < ulc_y < 17
                and 8 <= ulc_z < 17
            ):

                params = {
                    "bottom_right_corner": {
                        "x": btc_x,
                        "y": btc_y,
                        "z": btc_z,
                    },
                    "upper_left_corner": {
                        "x": ulc_x,
                        "y": ulc_y,
                        "z": ulc_z,
                    },
                    "steps": {
                        "z_step": z_step,
                    },
                    "folder": self.path_input.text(),
                    "folder prefix": self.folder_prefix_input.text(),
                    "freq": float(self.freq_input.text()),
                    "duration": d,
                }

                with open(
                    self.filepath,
                    "w",
                ) as file:
                    yaml.dump(
                        params,
                        file,
                        default_flow_style=False,
                    )
                self.disp_label.setText("Parameters saved !")

            else:
                self.disp_label.setText("wrong parameter values")

        except ValueError:
            self.disp_label.setText("Parameters must be float")


if __name__ == "__main__":
    import os

    os.chdir("..")
    core = CMMCorePlus()
    core.loadSystemConfiguration(
        r"C:\Program Files\Micro-Manager-2.0\Hamamatsu\orcaflash4.cfg"
    )
    pi_controller = PiController()
    app = napari.Viewer()

    widget = ScanBTNWidget(pi_controller, core)
    app.window.add_dock_widget(widget, area="left")

    Fwidget = FastScanBTNWidget(pi_controller, core)

    app.window.add_dock_widget(
        Fwidget,
        area="left",
    )

    napari.run()
