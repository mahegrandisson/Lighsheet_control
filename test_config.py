import PyDAQmx
from PyDAQmx import (
    Task,
)
from pulsing import (
    generate_sin_wave,
)
import time
import numpy as np
from simple_galvo import (
    set_galvos_position,
)

frequency = 20
# frequency = frequency*2
duration = 2


step_cam = 1 / (2 * frequency)


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
    1,
)
taskCAM.CfgDigEdgeStartTrig(
    "/Dev1/PFI12",
    PyDAQmx.DAQmx_Val_Rising,
)

time_per_value = int(1000 / frequency)
samples_per_period = 1000
sample_rate = samples_per_period * frequency
time_per_period = 1 / frequency
wave_2 = generate_sin_wave(
    -0.5,
    0.5,
    frequency * 10,
    duration,
    sample_rate,
)

taskG.CfgSampClkTiming(
    "/Dev1/PFI12",
    sample_rate,
    PyDAQmx.DAQmx_Val_Rising,
    PyDAQmx.DAQmx_Val_ContSamps,
    samples_per_period,
)


task_ms = Task()
task_ms.CreateCOPulseChanTime(
    "/Dev1/ctr0",
    "",
    PyDAQmx.DAQmx_Val_Seconds,
    PyDAQmx.DAQmx_Val_Low,
    0,
    time_per_period / (2 * samples_per_period),
    time_per_period / (2 * samples_per_period),
)
task_ms.CfgImplicitTiming(
    PyDAQmx.DAQmx_Val_ContSamps,
    1,
)
print(wave_2.shape)
taskG.WriteAnalogF64(
    len(wave_2),
    False,
    10.0,
    PyDAQmx.DAQmx_Val_GroupByChannel,
    wave_2,
    None,
    None,
)

taskG.StartTask()
taskCAM.StartTask()
task_ms.StartTask()

time.sleep(duration)

task_ms.StopTask()
task_ms.ClearTask()
taskG.StopTask()
taskG.ClearTask()
taskCAM.StopTask()
taskCAM.ClearTask()
set_galvos_position(0, 0)
