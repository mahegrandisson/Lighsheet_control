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

    # Calcul de la période et du temps entre les échantillons
    period = 1 / freq  # Période de l'onde en secondes
    total_time = cycles_per_buffer * period  # Temps total pour les cycles

    # Créer un vecteur de temps
    time_array = np.linspace(0, total_time, samples_per_buffer, endpoint=False)

    # Générer la sine wave
    sine_wave = amp * np.sin(2 * np.pi * freq * time_array) + offset

    return sine_wave


def scan_between_galvos(start1, end1, start2, end2, steps):
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
        "Dev1/ao0", "", start1, end1, PyDAQmx.DAQmx_Val_Volts, None
    )

    task2 = Task()
    task2.CreateAOVoltageChan(
        "Dev1/ao1", "", start2, end2, PyDAQmx.DAQmx_Val_Volts, None
    )

    galvo1_values = np.linspace(start1, end1, steps)
    galvo2_values = np.linspace(start2, end2, steps)

    # Balayage 2D
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

    # Créer les tâches pour les deux galvanomètres
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
    task2.WriteAnalogF64(
        len(np.arange(start2, end2, step)),
        True,
        10.0,
        PyDAQmx.DAQmx_Val_GroupByChannel,
        np.arange(start2, end2, step),
        None,
        None,
    )
    task2.WriteAnalogF64(
        len(np.arange(start2, end2, step)),
        True,
        10.0,
        PyDAQmx.DAQmx_Val_GroupByChannel,
        np.arange(end2, start2, -step),
        None,
        None,
    )
    tmp = time.time()
    print(tmp - tm)


# Paramètres d'entrée
"""
offset_val_1 = -0.01
offset_val_2 = 0
samples_per_buffer=750

# Générer l'onde
sine_wave_1 = generate_sine_wave(offset=offset_val_1)
sine_wave_2 = generate_sine_wave(offset=offset_val_2)

task_1 = Task()
task_2 = Task()
task_1.CreateAOVoltageChan("Dev1/ao0","",-0.2,-0.010,PyDAQmx.DAQmx_Val_Volts,None) #mouvement horizontal (+ -> vers objectif)
task_2.CreateAOVoltageChan("Dev1/ao1","",-5,5,PyDAQmx.DAQmx_Val_Volts,None) #mouvement vertical (+ -> vers le bas)
task_1.WriteAnalogF64(samples_per_buffer,True,10,PyDAQmx.DAQmx_Val_GroupByChannel,sine_wave_1,None,None)
task_2.WriteAnalogF64(samples_per_buffer,True,10,PyDAQmx.DAQmx_Val_GroupByChannel,sine_wave_2,None,None)

task_1.StopTask()
task_1.ClearTask()

task_2.StopTask()
task_2.ClearTask()
"""
if __name__ == "__main__":
    print("tasks running...")
    # scan_between_galvos(-0.1, -0.02, -3, 3, 10)
    # sweep_vert(0,-1,1,0.1)

    print("all of the tasks have succeeded")
