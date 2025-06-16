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
    Generates a sine wave with a given offset in meters.

    Parameters:
    - offset (float): Offset of the wave in meters.
    - amp (float): Amplitude of the wave in meters. Default is 0.
    - freq (float): Frequency of the wave in Hz. Default is 1 Hz.
    - samples_per_buffer (int): Number of samples per buffer.
    - cycles_per_buffer (int): Number of cycles in the waveform.
    - sampling_rate (int): Sampling rate in Hz.

    Returns:
    - np.ndarray: Array of sine wave values.
    """
    period = 1 / freq  # Wave period in seconds
    total_time = cycles_per_buffer * period  # Total time duration

    # Create a time vector
    time_array = np.linspace(0, total_time, samples_per_buffer, endpoint=False)

    # Generate sine wave
    sine_wave = amp * np.sin(2 * np.pi * freq * time_array) + offset

    return sine_wave


def scan_between_galvos(start1, end1, start2, end2, steps):
    """
    Performs a scan across the defined voltage ranges for two galvos.

    For each position of Galvo 1, the function sweeps across all positions of Galvo 2.

    Parameters:
    - start1 (float): Minimum voltage for Galvo 1.
    - end1 (float): Maximum voltage for Galvo 1.
    - start2 (float): Minimum voltage for Galvo 2.
    - end2 (float): Maximum voltage for Galvo 2.
    - steps (int): Number of positions (steps) per galvo.
    """
    task1 = Task()
    task1.CreateAOVoltageChan("Dev1/ao0", "", start1, end1, PyDAQmx.DAQmx_Val_Volts, None)

    task2 = Task()
    task2.CreateAOVoltageChan("Dev1/ao1", "", start2, end2, PyDAQmx.DAQmx_Val_Volts, None)

    galvo1_values = np.linspace(start1, end1, steps)
    galvo2_values = np.linspace(start2, end2, steps)

    # 2D scanning loop
    for value1 in galvo1_values:
        print(f"Galvo 1 position: {value1}")
        sine_wave_1 = generate_sine_wave(offset=value1)
        task1.WriteAnalogF64(
            1,
            True,
            10.0,
            PyDAQmx.DAQmx_Val_GroupByChannel,
            sine_wave_1,
            None,
            None,
        )
        for value2 in galvo2_values:
            sine_wave_2 = generate_sine_wave(offset=value2)
            task2.WriteAnalogF64(
                1,
                True,
                10.0,
                PyDAQmx.DAQmx_Val_GroupByChannel,
                sine_wave_2,
                None,
                None,
            )
            time.sleep(0.5)

    # Clean up tasks
    task1.StopTask()
    task1.ClearTask()
    task2.StopTask()
    task2.ClearTask()


if __name__ == "__main__":
    # Create a task for analog input (e.g., photodiode or sensor signal)
    task1 = Task()
    task1.CreateAIVoltageChan(
        "Dev1/ai0",          # Analog input channel
        "",
        PyDAQmx.DAQmx_Val_Cfg_Default,
        -10.0,
        10.0,
        PyDAQmx.DAQmx_Val_Volts,
        None,
    )

    # Configure the sampling clock
    task1.CfgSampClkTiming(
        "",                       # Use onboard clock
        1000.0,                   # Sampling rate: 1000 samples/sec
        PyDAQmx.DAQmx_Val_Rising,
        PyDAQmx.DAQmx_Val_ContSamps,
        1,
    )

    task1.StartTask()

    # Read and display data continuously until interrupted
    try:
        while True:
            data = np.zeros(1, dtype=np.float64)
            task1.ReadAnalogF64(
                1,
                10.0,
                PyDAQmx.DAQmx_Val_GroupByChannel,
                data,
                len(data),
                None,
                None,
            )
            print("Measured value (V):", data[0])
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Data acquisition stopped by user.")

    finally:
        task1.StopTask()
        task1.ClearTask()
