import PyDAQmx
import numpy as np
import time
from PyDAQmx import Task


def switch_mirror(state: int):
    task = Task()
    task.CreateDOChan("Dev1/port0/line0", "", PyDAQmx.DAQmx_Val_ChanForAllLines)

    try:
            if state==1 or state==0:
                data = np.array([state], dtype=np.uint8)
                task.WriteDigitalLines(1, 1, 10.0, PyDAQmx.DAQmx_Val_GroupByChannel, data, None, None)
                time.sleep(2)
    finally:
        task.StopTask()
        task.ClearTask()


if __name__=="__main__":
    switch_mirror(1)

    switch_mirror(0)
