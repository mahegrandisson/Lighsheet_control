import ctypes as ct
import time

import numpy as np
from PyDAQmx import (
    Task,
)
import PyDAQmx
from pi_contol.PiController import (
    PiController,
)

task = Task()


samples_per_cycle = (
    1  # Nombre d'échantillons par cycle (1 échantillon à chaque impulsion)
)


task.CreateDOChan(
    "Dev1/port0/line0",
    "",
    PyDAQmx.DAQmx_Val_ChanForAllLines,
)


# task.CfgSampClkTiming("", frequency, PyDAQmx.DAQmx_Val_Rising,
# PyDAQmx.DAQmx_Val_ContSamps, samples_per_cycle)

pi_controller = PiController()
pi_controller.move_abs(1, 11)
pi_controller.move_abs(2, 80)
pi_controller.move_abs(
    3,
    14.35,
)
pi_controller.move_abs(
    4,
    16.5,
)
time.sleep(2)
print("init done")
samples_written = ct.c_int32()
times = []
task.StartTask()
for _ in range(40):
    tmp = time.time()
    times.append(tmp)
    task.WriteDigitalLines(
        samples_per_cycle,
        True,
        10.0,
        PyDAQmx.DAQmx_Val_GroupByChannel,
        np.array(
            [1],
            dtype=np.uint8,
        ),
        ct.byref(samples_written),
        None,
    )

    task.WriteDigitalLines(
        samples_per_cycle,
        True,
        10.0,
        PyDAQmx.DAQmx_Val_GroupByChannel,
        np.array(
            [0],
            dtype=np.uint8,
        ),
        ct.byref(samples_written),
        None,
    )
    time.sleep(0.008)  # 20 fps 50ms*2
    # time.sleep(0.098) #5(fps)
    # time.sleep(1) #0.5(fps)

    # pi_controller.move_rel(4,-0.01)
    # time.sleep(0.1)
    # task.StopTask()


task.ClearTask()
print(times)
