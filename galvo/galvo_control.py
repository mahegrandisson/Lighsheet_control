import numpy as np
import PyDAQmx
from PyDAQmx import (
    Task,
)


def set_galvos_position(
    value: float,
    galvo_id: int,
):
    """
    Sets the voltage position of a specific galvo mirror via the DAQ device.

    Parameters:
    - value: Voltage to send to the galvo (must be within the range -5V to 5V).
    - galvo_id: Identifier of the galvo to control.
        - 1 → controls galvo on channel ao0
        - 2 → controls galvo on channel ao1

    Notes:
    - Only galvo_id values of 1 or 2 are valid.
    - Automatically opens and closes the DAQ task.
    """

    task = Task()
    if galvo_id in [
        1,
        2,
    ]:
        if galvo_id == 1:
            task.CreateAOVoltageChan(
                "Dev1/ao0",
                "",
                -5,
                5,
                PyDAQmx.DAQmx_Val_Volts,
                None,
            )
        else:
            task.CreateAOVoltageChan(
                "Dev1/ao1",
                "",
                -5,
                5,
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
