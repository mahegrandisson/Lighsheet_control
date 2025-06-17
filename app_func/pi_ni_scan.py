import numpy as np
from tifffile import (
    tifffile,
)
from ome_types import (
    from_xml,
)
from pi_contol.PiController import (
    PiController,
)
from PyDAQmx import (
    Task,
)
import PyDAQmx

from testing.pulsing import generate_sin_wave

import time
from pymmcore_plus import (
    CMMCorePlus,
)
from pipython import (
    PILogger,
)
import logging
from skimage.io import (
    imsave,
)
from napari.qt.threading import (
    thread_worker,
)
import os


@thread_worker
def scan(
    pi_controller: PiController,
    core: CMMCorePlus,
    device_id: int,
    startZ: float,
    stopZ: float,
    startY: float,
    stopY: float,
    plane_number: int,
    frequency: float,
    sample_number_per_sine_period: int,
    path: str,
    duration: float = 2,
):
    """
    Performs a Z-axis scan while sending a sinusoidal signal to the galvo (Y-axis).

    Parameters:
    - pi_controller: Instance of PiController to control PI devices.
    - device_id: Index of the PI device to use (1-based index).
    - startZ: Starting position on the Z-axis.
    - stopZ: Ending position on the Z-axis.
    - startY: Starting position for the galvo (Y-axis).
    - stopY: Ending position for the galvo (Y-axis).
    - plane_number: Number of image planes to capture along the Z-axis.
    - frequency: Frequency of the sinusoidal wave used to modulate the galvo.
    - sample_number_per_sine_period: Number of samples per sine wave period.
    - duration: Duration of the scan in seconds (default is 120).
    """

    taskG = Task()
    taskG.CreateAOVoltageChan(
        "Dev1/ao1",
        "",
        -10,
        10,
        PyDAQmx.DAQmx_Val_Volts,
        None,
    )
    taskG.CfgDigEdgeStartTrig(
        "/Dev1/PFI12",
        PyDAQmx.DAQmx_Val_Rising,
    )

    samples_per_period = sample_number_per_sine_period
    sample_rate = samples_per_period * frequency
    taskG.CfgSampClkTiming(
        "/Dev1/PFI12",
        sample_rate,
        PyDAQmx.DAQmx_Val_Rising,
        PyDAQmx.DAQmx_Val_ContSamps,
        samples_per_period,
    )

    task_ms = Task()
    time_per_period = 1 / frequency
    step_val = time_per_period / (2 * samples_per_period)
    task_ms.CreateCOPulseChanTime(
        "/Dev1/ctr0",
        "",
        PyDAQmx.DAQmx_Val_Seconds,
        PyDAQmx.DAQmx_Val_Low,
        0,
        step_val,
        step_val,
    )
    task_ms.CfgImplicitTiming(
        PyDAQmx.DAQmx_Val_ContSamps,
        1,
    )

    data = generate_sin_wave(
        startY,
        stopY,
        frequency * 10,
        duration,
        sample_rate,
    )
    fifteen_percent = data[len(data) - int(0.2 * len(data)) :]
    # print(fifteen_percent.shape)
    # print(data.shape)
    data = np.concatenate(
        (
            data,
            fifteen_percent,
        )
    )
    # data.shape)
    taskG.WriteAnalogF64(
        len(data),
        False,
        10.0,
        PyDAQmx.DAQmx_Val_GroupByChannel,
        data,
        None,
        None,
    )

    axe = 1
    pi_controller.devices[device_id - 1].gcscommands.VEL(
        axe,
        1.5,
    )

    pi_controller.devices[device_id - 1].gcscommands.MOV(
        axe,
        startZ,
    )
    while not pi_controller.devices[device_id - 1].gcscommands.qONT(axe)[axe]:
        time.sleep(0.05)
    # print(pi_controller.devices[device_id-1].gcscommands.qONT(axe)[axe])
    planes = np.linspace(
        startZ,
        stopZ,
        plane_number,
    )

    images = []
    taskG.StartTask()
    task_ms.StartTask()

    for i in range(plane_number):
        pi_controller.devices[device_id - 1].gcscommands.MOV(
            axe,
            planes[i],
        )
        while not pi_controller.devices[device_id - 1].gcscommands.qONT(axe)[axe]:
            time.sleep(0.05)
        im = core.snap(fix=True)
        images.append(im)

    taskG.StopTask()
    task_ms.StopTask()
    taskG.ClearTask()
    task_ms.ClearTask()

    for i in range(len(images)):
        s = path + "/" + str(i) + ".tif"
        imsave(
            s,
            images[i],
        )


def sync_scan(
    pi_controller: PiController,
    device_id: int,
    core: CMMCorePlus,
    startZ: float,
    stopZ: float,
    startY: float,
    stopY: float,
    frequency: float,
    plane_size: int,
    plane_number: int,
):
    """
    Performs a synchronous scan by moving the galvo (Y) and the Z-stage.

    Parameters:
    - pi_controller: PI controller instance.
    - device_id: Index of the PI device to use.
    - core: Micro-Manager CMMCorePlus object for image acquisition.
    - startZ: Starting position along the Z-axis.
    - stopZ: Ending position along the Z-axis.
    - startY: Starting galvo position (Y-axis).
    - stopY: Ending galvo position.
    - frequency: Used to determine timing and spacing.
    - plane_size: Number of images per Z-slice (Y-steps).
    - plane_number: Number of Z-slices (planes).
    """

    axe = 1
    # a changer -----------------------------------------
    step_cam = 1 / (2 * frequency)
    taskCAM = Task()
    taskCAM.CreateCOPulseChanTime(
        "/Dev1/ctr1",
        "",
        PyDAQmx.DAQmx_Val_Seconds,
        PyDAQmx.DAQmx_Val_Low,
        0,
        step_cam,
        step_cam,
    )
    taskCAM.CfgImplicitTiming(
        PyDAQmx.DAQmx_Val_ContSamps,
        0,
    )
    taskCAM.CfgDigEdgeStartTrig(
        "/Dev1/PFI12",
        PyDAQmx.DAQmx_Val_Rising,
    )
    # --------------------------------------------------------
    taskG = Task()
    taskG.CreateAOVoltageChan(
        "Dev1/ao1",
        "",
        -10,
        10,
        PyDAQmx.DAQmx_Val_Volts,
        None,
    )

    dataG = np.linspace(
        startY,
        stopY,
        plane_size,
    )
    dataPI = np.linspace(
        startZ,
        stopZ,
        plane_number,
    )
    images = []

    for i in range(plane_number):
        pi_controller.devices[device_id - 1].gcscommands.MOV(
            axe,
            dataPI[i],
        )
        while not pi_controller.devices[device_id - 1].gcscommands.qONT(axe)[axe]:
            time.sleep(0.05)

        for j in range(plane_size):
            taskG.WriteAnalogF64(
                1,
                True,
                10.0,
                PyDAQmx.DAQmx_Val_GroupByChannel,
                np.array(dataG[j]),
                None,
                None,
            )
            im = core.snap(fix=True)
            images.append(im)

    taskG.StopTask()

    # taskCAM.StopTask
    taskG.ClearTask()

    taskCAM.ClearTask()

    for i in range(len(images)):
        s = "TEST/" + str(i + 1) + ".tif"
        imsave(
            s,
            images[i],
        )


@thread_worker
def brillouin_scan(
    pi_controller: PiController,
    core: CMMCorePlus,
    starting_point_x,
    starting_point_y,
    starting_point_z,
    end_point_x,
    end_point_y,
    end_point_z,
    step_x,
    step_y,
    step_z,
    path,
):
    """
    Executes a full 3D Brillouin scan using serpentine scanning pattern.

    Parameters:
    - pi_controller: Controller instance for PI XYZ stages.
    - core: Micro-Manager core object for controlling the camera and hardware.
    - starting_point_x/y/z: Starting positions for each axis.
    - end_point_x/y/z: Ending positions for each axis.
    - step_x/y/z: Step size for each axis (in micrometers, will be converted to mm internally).
    - path: Directory path where acquired OME-TIFF images will be saved.
    """

    axe = 1
    step_z = step_x / 1000
    step_x = step_x / 1000
    step_y = step_y / 1000
    pi_controller.devices[0].gcscommands.VEL(
        axe,
        1.5,
    )  # z
    pi_controller.devices[2].gcscommands.VEL(
        axe,
        1.5,
    )  # x
    pi_controller.devices[3].gcscommands.VEL(
        axe,
        1.5,
    )  # y

    num_z_values = int(abs((end_point_z - starting_point_z) // step_z)) + 1
    num_x_values = int(abs((end_point_x - starting_point_x) // step_x)) + 1
    num_y_values = int(abs((end_point_y - starting_point_y) // step_y)) + 1

    # print(num_z_values,num_x_values,num_y_values)

    dataPI_z = np.linspace(
        starting_point_z,
        end_point_z,
        num_z_values,
    )
    dataPI_x = np.linspace(
        starting_point_x,
        end_point_x,
        num_x_values,
    )
    dataPI_y = np.linspace(
        starting_point_y,
        end_point_y,
        num_y_values,
    )

    core.setROI(
        0,
        0,
        1000,
        1000,
    )

    # print(dataPI_z,dataPI_x,dataPI_y)

    images = []

    pi_controller.devices[0].gcscommands.MOV(
        axe,
        starting_point_z,
    )
    pi_controller.devices[2].gcscommands.MOV(
        axe,
        starting_point_x,
    )
    pi_controller.devices[3].gcscommands.MOV(
        axe,
        starting_point_y,
    )

    while not pi_controller.devices[0].gcscommands.qONT(axe)[axe]:
        time.sleep(0.005)
    while not pi_controller.devices[2].gcscommands.qONT(axe)[axe]:
        time.sleep(0.005)
    while not pi_controller.devices[3].gcscommands.qONT(axe)[axe]:
        time.sleep(0.005)

    for i in range(num_z_values):
        # if i!=0 :
        # move_z = 0.9 * (dataPI_z[i] - dataPI_z[i-1]) + dataPI_z[i-1]
        # pi_controller.devices[0].gcscommands.MOV(axe, move_z)
        # else:
        pi_controller.devices[0].gcscommands.MOV(
            axe,
            dataPI_z[i],
        )

        # print("Z",pi_controller.devices[0].gcscommands.qPOS(axe))

        for j in range(num_x_values):
            #    if j!=0:
            #        move_x = 0.9 * (dataPI_x[j] - dataPI_x[j-1]) + dataPI_x[j-1]
            #        pi_controller.devices[2].gcscommands.MOV(axe, move_x)
            #    else:
            pi_controller.devices[2].gcscommands.MOV(
                axe,
                dataPI_x[j],
            )

            # print("X",pi_controller.devices[2].gcscommands.qPOS(axe))

            for k in range(num_y_values):

                # if k!=0:
                #    move_y = 0.9 * (dataPI_y[k] - dataPI_y[k-1]) + dataPI_y[k-1]
                #    pi_controller.devices[3].gcscommands.MOV(axe, move_y)
                # else:
                if j % 2 == 0:
                    pi_controller.devices[3].gcscommands.MOV(
                        axe,
                        dataPI_y[k],
                    )
                else:
                    pi_controller.devices[3].gcscommands.MOV(
                        axe,
                        dataPI_y[num_y_values - 1 - k],
                    )

                while not pi_controller.devices[3].gcscommands.qONT(axe)[axe]:
                    time.sleep(0.005)
                if k == 0:
                    while not pi_controller.devices[0].gcscommands.qONT(axe)[axe]:
                        time.sleep(0.005)
                    while not pi_controller.devices[2].gcscommands.qONT(axe)[axe]:
                        time.sleep(0.005)

                # print("Y", pi_controller.devices[3].gcscommands.qPOS(axe))

                im = core.snap(fix=True)
                if j % 2 == 0:
                    images.append(
                        [
                            dataPI_x[j],
                            dataPI_y[k],
                            dataPI_z[i],
                            im,
                            step_z,
                        ]
                    )
                else:
                    images.append(
                        [
                            dataPI_x[j],
                            dataPI_y[num_y_values - 1 - k],
                            dataPI_z[i],
                            im,
                            step_z,
                        ]
                    )

    save_images(
        images,
        path,
    )


def save_images(
    images,
    path,
):
    """
    Saves the acquired images as OME-TIFF files, embedding spatial metadata.

    Parameters:
    - images: A list of elements [X, Y, Z, image, spacing] for each voxel.
    - path: Destination folder where TIFF images will be stored.
    """

    if not os.path.exists(path):
        os.makedirs(path)
    for i in range(len(images)):
        x_pos = int(images[i][0] * 1e3)
        y_pos = int(images[i][1] * 1e3)
        z_pos = int(images[i][2] * 1e3)
        img = images[i][3]
        spacing = images[i][4]
        tifffile.imwrite(
            path
            + "/"
            + "Z"
            + str(z_pos)
            + "_X"
            + str(x_pos)
            + "_Y"
            + str(y_pos)
            + ".ome.tif",
            img,
            ome=True,
            metadata={
                "axes": "YX",
                "spacing": spacing,
                "unit": "µm",
                "Plane": {
                    "PositionX": x_pos,
                    "PositionY": y_pos,
                    "PositionZ": z_pos,
                    "PositionXUnit": "µm",
                    "PositionYUnit": "µm",
                    "PositionZUnit": "µm",
                },
            },
        )


def read_tiff_img(
    img: str,
):
    """
    Reads a TIFF image file and extracts its OME metadata.

    Parameters:
    - img: Path to the TIFF file.

    Returns:
    - Tuple of (OME metadata as parsed object, image data as numpy array).
    """

    with tifffile.TiffFile(img) as tif:
        image_data = tif.asarray()
        metadata = tif.ome_metadata
        ome_dict = from_xml(metadata)
        # print(ome_dict.images[0].pixels.planes[0].position_x)
    return (
        ome_dict.images[0],
        image_data,
    )


if __name__ == "__main__":
    PILogger.setLevel(logging.CRITICAL + 1)  # deactivate PILogger
    core = CMMCorePlus()
    core.loadSystemConfiguration(
        r"C:\Program Files\Micro-Manager-2.0\Hamamatsu\orcaflash4.cfg"
    )
    core.setExposure(20)
    pi_controller = PiController()
    scan(pi_controller, 1, 10, 12, -0.5, 0.5, 10, 20, 10000)
    # set_galvos_position(0,0)
    # sync_scan(pi_controller,1,core,10,12,-0.5,0.5,20,10,10)
    """brillouin_scan(
        pi_controller,
        core,
        12,
        10,
        15,
        12.5,
        11.5,
        15.04,
        100,
        100,
        20,
        "../images/Brillouin_Tiff",
    )"""
