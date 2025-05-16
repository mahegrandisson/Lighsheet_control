import time
import PyDAQmx
from PyDAQmx import (
    Task,
)
import numpy as np
from galvo_control import set_galvos_position


def generate_sin_wave(
    start_value,
    end_value,
    frequency,
    duration: float,
    sampling_rate=1000,
):

    t = np.linspace(
        0,
        duration,
        sampling_rate * duration,
        endpoint=False,
    )

    amplitude = (start_value - end_value) / 2

    sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return sine_wave


def fast_fluo(
    frequency,
    duration,
    sine_start: float,
    sine_stop: float,
    sample_number_per_sine_period=10000,
):

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

    taskG = Task()
    taskG.CreateAOVoltageChan(
        "Dev1/ao0",
        "",
        -10,
        10,
        PyDAQmx.DAQmx_Val_Volts,
        None,
    )
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

    wave_2 = generate_sin_wave(
        -0.5,
        0.5,
        frequency * 10,
        duration,
        sample_rate,
    )
    dataG = np.zeros(
        (
            len(wave_2),
            2,
        )
    )

    period_duration = int(len(wave_2) * time_per_period / duration)
    wave_1 = np.linspace(
        sine_start,
        sine_stop,
        len(wave_2),
    )

    for i in range(
        0,
        len(wave_1),
        period_duration,
    ):
        wave_1[i : i + period_duration] = wave_1[i]

    dataG[
        :,
        0,
    ] = wave_1
    dataG[
        :,
        1,
    ] = wave_2

    # tm = time.time()

    taskG.WriteAnalogF64(
        len(wave_2),
        False,
        10.0,
        PyDAQmx.DAQmx_Val_GroupByScanNumber,
        dataG,
        None,
        None,
    )
    taskG.StartTask()
    taskCAM.StartTask()
    task_ms.StartTask()
    # tmp = time.time()
    # print(tmp - tm)

    time.sleep(duration)

    task_ms.StopTask()
    task_ms.ClearTask()
    taskG.StopTask()
    taskG.ClearTask()
    taskCAM.StopTask()
    taskCAM.ClearTask()
    set_galvos_position(
        0,
        0,
    )


if __name__ == "__main__":
    sample_number_per_sine_period = 10000
    frequency = 20
    duration = 2
    sine_start = -0.04
    sine_stop = 0.05
    fast_fluo(
        frequency,
        duration,
        sine_start,
        sine_stop,
        sample_number_per_sine_period=10000,
    )
