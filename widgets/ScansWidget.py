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
from PyQt5.QtCore import (
    Qt,
)
import napari
import os
from pymmcore_plus import (
    CMMCorePlus,
)
from pi_contol.PiController import (
    PiController,
)
from app_func.pi_ni_scan import (
    brillouin_scan,
)
from app_func.app_functions import (
    B_PARAMS,
)


class ScanBTNWidget(QWidget):
    def __init__(
        self,
        pi_controller,
        core,
    ):
        super().__init__()
        self.brillouin_widget = ScanWidget(
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
            "Scan parameters",
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
            lambda: self.toggle_widget(self.brillouin_widget)
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
    def __init__(
        self,
        pi_controller: PiController,
        core: CMMCorePlus,
    ):
        super().__init__()
        self.hidden = True
        self.pi_controller = pi_controller
        self.core = core

        # define the system's available cameras
        self.cameras = []
        self.cam_names = ["ORCA","CAM"]
        print(self.core.getLoadedDevices())
        for dev in self.core.getLoadedDevices():
            for name in self.cam_names:
                if name in dev.upper():
                    self.cameras.append(dev)


        # where to save the scan params
        self.filepath = B_PARAMS
        self.full_path = ""
        # safety init
        (
            self.start_z,
            self.end_z,
        ) = (
            16.99,
            16.99,
        )
        (
            self.start_x,
            self.end_x,
        ) = (
            8,
            8,
        )
        (
            self.start_x,
            self.end_x,
        ) = (
            8,
            8,
        )
        (
            self.start_y,
            self.end_y,
        ) = (
            14,
            14,
        )

        # display
        self.setWindowTitle("Scan parameters")
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
            "Scan Parameters",
            self,
        )
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignCenter)

        form_layout = QFormLayout()

        self.bottom_right_input = QLineEdit()
        self.upper_left_input = QLineEdit()
        self.x_step_input = QLineEdit()
        self.y_step_input = QLineEdit()
        self.z_step_input = QLineEdit()
        self.exposure_input = QLineEdit()
        self.camera_input = QComboBox()
        self.camera_input.addItems(self.cameras)
        self.camera_input.setCurrentText(self.core.getCameraDevice())

        self.info_label = QLabel()
        self.info_label.setText("4<=X<17   |   0<Y<17   |   8<=Z<17")
        self.info_label.setStyleSheet("color: pink;font-family: 'Arial Black';font-weight: bold;")

        grid_layout = QGridLayout()

        grid_layout.addWidget(
            QLabel("Bottom Right Cube Corner:"),
            0,
            0,
        )

        grid_layout.addWidget(
            QLabel("X (mm):"),
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
            QLabel("Y (mm):"),
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
            QLabel("Z (mm):"),
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
            QLabel("Upper Left Cube Corner:"),
            1,
            0,
        )

        grid_layout.addWidget(
            QLabel("X (mm):"),
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
            QLabel("Y (mm):"),
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
            QLabel("Z (mm):"),
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
            "X Step (µm):",
            self.x_step_input,
        )
        form_layout.addRow(
            "Y Step (µm):",
            self.y_step_input,
        )
        form_layout.addRow(
            "Z Step (µm):",
            self.z_step_input,
        )
        form_layout.addRow(
            "camera:",
            self.camera_input,
        )
        form_layout.addRow(
            "exposure (ms):",
            self.exposure_input,
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
        self.info_label_2.setStyleSheet("color: pink;font-family: 'Arial Black';font-weight: bold;")

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

            s_x = float(self.x_step_input.text())
            s_y = float(self.y_step_input.text())
            s_z = float(self.z_step_input.text())

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
                        "x_step": s_x,
                        "y_step": s_y,
                        "z_step": s_z,
                    },
                    "folder": self.path_input.text(),
                    "folder prefix": self.folder_prefix_input.text(),
                    "exposure": float(self.exposure_input.text()),
                    "camera": self.camera_input.currentText(),
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

            self.x_step_input.setText(str(params["steps"]["x_step"]))
            self.y_step_input.setText(str(params["steps"]["y_step"]))
            self.z_step_input.setText(str(params["steps"]["z_step"]))

            self.path_input.setText(params["folder"])

            self.folder_prefix_input.setText(params["folder prefix"])
            if params["camera"] != "":
                self.camera_input.setCurrentText(params["camera"])
            else:
                self.camera_input.setCurrentText(self.cameras[0])



            self.exposure_input.setText(str(params["exposure"]))

            self.disp_label.setText("Parameters loaded.")

        except Exception as e:
            self.disp_label.setText(f"Failed to load parameters: {e}")

    def run_scan(
        self,
    ):
        try:
            self.core.setExposure(float(self.exposure_input.text()))
            # if self.disp_label.text() == "Parameters saved !":
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

            self.disp_label.setText("running and computing...")
            self.full_path = (
                self.path_input.text() + "/" + self.folder_prefix_input.text()
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


if __name__ == "__main__":
    core = CMMCorePlus()
    core.loadSystemConfiguration(
        r"C:\Program Files\Micro-Manager-2.0\Hamamatsu\orcaflash4.cfg"
    )
    pi_controller = PiController()
    app = napari.Viewer()
    widget = ScanBTNWidget(
        pi_controller,
        core,
    )
    app.window.add_dock_widget(
        widget,
        area="left",
    )
    napari.run()
