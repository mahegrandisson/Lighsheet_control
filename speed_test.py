import PyDAQmx
from PIL import (
    Image,
)
import numpy as np
from PyDAQmx import (
    Task,
)
from pymmcore_plus import (
    CMMCorePlus,
)
from simple_galvo import (
    set_galvos_position,
)
import time
from PyQt5.QtCore import (
    pyqtSignal,
    QObject,
)


class NMM(QObject):
    mvmt_done = pyqtSignal()

    def __init__(
        self,
        config: str = r"C:\Program Files\Micro-Manager-2.0\PVCam\MMConfig_demo.cfg",
        exposure: int = 10,
    ):
        super().__init__()
        # self.viewer = napari.Viewer()
        self.core = CMMCorePlus()
        self.core.loadSystemConfiguration(config)
        self.core.setCameraDevice("Camera-1")
        self.core.setExposure(exposure)

    def snap(
        self,
        image_name: str,
    ):
        image = self.core.snap()
        img = Image.fromarray(image)
        img.save(image_name)

    def showDevices(
        self,
    ):
        print(
            "CAMERA=",
            self.core.getCameraDevice(),
        )
        print(
            "SLM=",
            self.core.getSLMDevice(),
        )

    def set_galvos_position(
        self,
        value: float,
        galvo_id: int,
    ):
        """
        Fonction pour envoyer des valeurs à deux galvanomètres en utilisant PyDAQmx.

        :param start1: Valeur pour le Galvo 1 (en Volts).
        :param start2: Valeur pour le Galvo 2 (en Volts).
        """
        # print(value)
        # print(galvo_id)
        task = Task()
        if galvo_id in [
            1,
            2,
        ]:
            if galvo_id == 1:
                task.CreateAOVoltageChan(
                    "Dev1/ao0",
                    "",
                    value,
                    value + 0.01,
                    PyDAQmx.DAQmx_Val_Volts,
                    None,
                )
            else:
                task.CreateAOVoltageChan(
                    "Dev1/ao1",
                    "",
                    value,
                    value + 0.01,
                    PyDAQmx.DAQmx_Val_Volts,
                    None,
                )
        else:
            print("Galvo id should be 1 or 2")
            return None
        try:

            data = np.array(
                [value],
                dtype=np.float64,
            )

            task.WriteAnalogF64(
                1,
                True,
                10.0,
                PyDAQmx.DAQmx_Val_GroupByChannel,
                data,
                None,
                None,
            )
            # print("data envoyee:",data)

            # Fermer les tâches après l'écriture
            task.StopTask()
            task.ClearTask()

        except Exception as e:
            print(f"Error setting galvo positions: {e}")

    def save_image(
        self,
        filename,
        image_data,
    ):
        """
        Sauvegarder l'image sous forme de fichier .tif.
        """
        from skimage.io import (
            imsave,
        )

        imsave(
            filename,
            image_data,
        )

    def test(
        self,
    ):
        mvmt_done = pyqtSignal()

    def snapping(
        self,
    ):
        self.core.snapImage()
        im = self.core.getImage()

    def scan_between_galvos(
        self,
        start1,
        end1,
        start2,
        end2,
        steps,
        folder="TEST",
    ):
        """
        Effectue un balayage entre les bornes des deux galvanomètres.
        Pour chaque point de Galvo1, on parcourt toute la plage de Galvo2.

        :param start1: Valeur minimale pour le Galvo 1.
        :param end1: Valeur maximale pour le Galvo 1.
        :param start2: Valeur minimale pour le Galvo 2.
        :param end2: Valeur maximale pour le Galvo 2.
        :param steps: Nombre de points à échantillonner pour chaque galvo.
        """
        # Créer les tâches pour les deux galvanomètres
        task1 = Task()
        task1.CreateAOVoltageChan(
            "Dev1/ao0",
            "",
            start1,
            end1,
            PyDAQmx.DAQmx_Val_Volts,
            None,
        )

        task2 = Task()
        task2.CreateAOVoltageChan(
            "Dev1/ao1",
            "",
            start2,
            end2,
            PyDAQmx.DAQmx_Val_Volts,
            None,
        )

        galvo1_values = np.linspace(
            start1,
            end1,
            steps,
        )
        galvo2_values = np.linspace(
            start2,
            end2,
            steps,
        )

        (
            i,
            j,
        ) = (
            0,
            0,
        )
        for value1 in galvo1_values:
            i += 1
            j = 0
            data1 = np.array(
                [value1],
                dtype=np.float64,
            )
            task1.WriteAnalogF64(
                1,
                True,
                10.0,
                PyDAQmx.DAQmx_Val_GroupByChannel,
                data1,
                None,
                None,
            )
            for value2 in galvo2_values:
                j += 1
                data2 = np.array(
                    [value2],
                    dtype=np.float64,
                )
                task2.WriteAnalogF64(
                    1,
                    True,
                    10.0,
                    PyDAQmx.DAQmx_Val_GroupByChannel,
                    data2,
                    None,
                    None,
                )
                self.mvmt_done.emit()

        set_galvos_position(
            0,
            0,
        )

        task1.StopTask()
        task1.ClearTask()
        task2.StopTask()
        task2.ClearTask()


if __name__ == "__main__":
    nmm = NMM()
    nmm.mvmt_done.connect(nmm.snapping)
    nmm.scan_between_galvos(
        -0.03,
        0.03,
        -2,
        2,
        10,
    )
    # nmm.test()
