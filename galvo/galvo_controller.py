import PyDAQmx
import numpy as np
from PyDAQmx import Task
import time


def generate_sine_wave(
    offset: float,
    amp=0,
    freq=1,
    samples_per_buffer=750,
    cycles_per_buffer=15,
    sampling_rate=10000,
):
    """
    Generates a sine wave with a given offset, amplitude, and frequency.

    Parameters:
    - offset: DC offset of the sine wave.
    - amp: Amplitude of the sine wave.
    - freq: Frequency of the sine wave (Hz).
    - samples_per_buffer: Number of samples per buffer.
    - cycles_per_buffer: Number of sine cycles in the buffer.
    - sampling_rate: Sampling rate in Hz.

    Returns:
    - sine_wave: NumPy array containing the sine wave values.
    """
    period = 1 / freq  # Period of one cycle
    total_time = cycles_per_buffer * period  # Total duration

    # Time vector
    time_array = np.linspace(0, total_time, samples_per_buffer, endpoint=False)

    # Sine wave generation
    sine_wave = amp * np.sin(2 * np.pi * freq * time_array) + offset

    return sine_wave


def scan_between_galvos(start1, end1, start2, end2, steps):
    """
    Performs a 2D scan by varying both galvo positions.

    For each value in galvo 1's range, it sweeps across all values in galvo 2's range.

    Parameters:
    - start1: Minimum value for Galvo 1.
    - end1: Maximum value for Galvo 1.
    - start2: Minimum value for Galvo 2.
    - end2: Maximum value for Galvo 2.
    - steps: Number of discrete steps for each galvo.
    """
    task1 = Task()
    task1.CreateAOVoltageChan(
        "Dev1/ao0", "", start1, end1, PyDAQmx.DAQmx_Val_Volts, None
    )

    task2 = Task()
    task2.CreateAOVoltageChan(
        "Dev1/ao1", "", start2, end2, PyDAQmx.DAQmx_Val_Volts, None
    )

    galvo1_values = np.linspace(start1, end1, steps)
    galvo2_values = np.linspace(start2, end2, steps)

    for value1 in galvo1_values:
        sine_wave_1 = generate_sine_wave(offset=value1)
        task1.WriteAnalogF64(
            1, True, 10.0, PyDAQmx.DAQmx_Val_GroupByChannel, sine_wave_1, None, None
        )
        for value2 in galvo2_values:
            sine_wave_2 = generate_sine_wave(offset=value2)
            task2.WriteAnalogF64(
                1, True, 10.0, PyDAQmx.DAQmx_Val_GroupByChannel, sine_wave_2, None, None
            )
            time.sleep(0.5)

    task1.StopTask()
    task1.ClearTask()
    task2.StopTask()
    task2.ClearTask()


def sweep_vert(start1, start2, end2, step):
    """
    Performs a vertical sweep with one galvo fixed and the other scanning up and down.

    Parameters:
    - start1: Static value for Galvo 1.
    - start2: Starting value for Galvo 2.
    - end2: Ending value for Galvo 2.
    - step: Step size for Galvo 2 movement.
    """
    task1 = Task()
    task1.CreateAOVoltageChan("Dev1/ao0", "", -10, 10, PyDAQmx.DAQmx_Val_Volts, None)

    task2 = Task()
    task2.CreateAOVoltageChan("Dev1/ao1", "", -10, 10, PyDAQmx.DAQmx_Val_Volts, None)

    tm = time.time()
    task1.WriteAnalogF64(
        1,
        True,
        10.0,
        PyDAQmx.DAQmx_Val_GroupByChannel,
        np.array([start1], dtype=np.float64),
        None,
        None,
    )

    # Sweep up
    values_up = np.arange(start2, end2, step)
    task2.WriteAnalogF64(
        len(values_up),
        True,
        10.0,
        PyDAQmx.DAQmx_Val_GroupByChannel,
        values_up,
        None,
        None,
    )

    # Sweep back down
    values_down = np.arange(end2, start2, -step)
    task2.WriteAnalogF64(
        len(values_down),
        True,
        10.0,
        PyDAQmx.DAQmx_Val_GroupByChannel,
        values_down,
        None,
        None,
    )

    tmp = time.time()
    print("Sweep duration:", tmp - tm, "seconds")


# Test block
"""
# Example parameters
offset_val_1 = -0.01
offset_val_2 = 0
samples_per_buffer = 750

# Generate sine waves
sine_wave_1 = generate_sine_wave(offset=offset_val_1)
sine_wave_2 = generate_sine_wave(offset=offset_val_2)

# Create tasks
task_1 = Task()
task_2 = Task()
task_1.CreateAOVoltageChan("Dev1/ao0", "", -0.2, -0.010, PyDAQmx.DAQmx_Val_Volts, None)  # horizontal movement
task_2.CreateAOVoltageChan("Dev1/ao1", "", -5, 5, PyDAQmx.DAQmx_Val_Volts, None)        # vertical movement

# Write waveforms
task_1.WriteAnalogF64(samples_per_buffer, True, 10, PyDAQmx.DAQmx_Val_GroupByChannel, sine_wave_1, None, None)
task_2.WriteAnalogF64(samples_per_buffer, True, 10, PyDAQmx.DAQmx_Val_GroupByChannel, sine_wave_2, None, None)

# Cleanup
task_1.StopTask()
task_1.ClearTask()
task_2.StopTask()
task_2.ClearTask()
"""

if __name__ == "__main__":
    print("Tasks running...")
    # Uncomment to run:
    # scan_between_galvos(-0.1, -0.02, -3, 3, 10)
    # sweep_vert(0, -1, 1, 0.1)
    print("All of the tasks have succeeded.")
