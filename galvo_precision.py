import PyDAQmx
import numpy as np
from PyDAQmx import (
    Task,
)
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
    Fonction pour générer une onde sinusoïdale avec un offset en mètres.

    :param amp: Amplitude de l'onde en mètres (m)
    :param freq: Fréquence de l'onde en Hz
    :param offset: Offset en mètres (m)
    :param samples_per_buffer: Nombre d'échantillons par buffer
    :param cycles_per_buffer: Nombre de cycles dans chaque buffer
    :param sampling_rate: Taux d'échantillonnage (en Hz)
    :return: Tableau de la forme d'onde à envoyer
    """

    # Calcul de la période et du temps entre les échantillons
    period = 1 / freq  # Période de l'onde en secondes
    total_time = cycles_per_buffer * period  # Temps total pour les cycles

    # Créer un vecteur de temps
    time_array = np.linspace(
        0,
        total_time,
        samples_per_buffer,
        endpoint=False,
    )

    # Générer la sine wave
    sine_wave = amp * np.sin(2 * np.pi * freq * time_array) + offset

    return sine_wave


def scan_between_galvos(
    start1,
    end1,
    start2,
    end2,
    steps,
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

    # Balayage 2D
    for value1 in galvo1_values:
        print(value1)
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

    task1.StopTask()
    task1.ClearTask()
    task2.StopTask()
    task2.ClearTask()


if __name__ == "__main__":
    task1 = Task()
    task1.CreateAIVoltageChan(
        "Dev1/ai0",
        "",  # "Dev1/ai0" pour le premier canal analogique (AI0)
        0,
        -10.0,
        10.0,  # Plage de tension de -10V à +10V
        PyDAQmx.DAQmx_Val_Volts,
        None,
    )
    task1.CfgSampClkTiming(
        "",
        1000.0,
        Task.CfgSampClkTiming.SampTimingMode_Internal,
    )
    task1.Start()

    # Lire les données
    try:
        while True:
            # Lire un échantillon à la fois (ajustez la taille du buffer si nécessaire)
            data = np.zeros(
                1,
                dtype=np.float64,
            )
            task1.ReadAnalogF64(
                1,
                10.0,
                0,
                data,
            )  # Lire un échantillon avec un timeout de 10 secondes

            # Afficher la valeur lue
            print(
                "Valeur lue (V) : ",
                data[0],
            )

            # Délai avant la prochaine lecture (ajustez selon vos besoins)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Arrêt de l'acquisition de données.")

    finally:
        # Arrêter et nettoyer la tâche
        task1.Stop()
        task1.Clear()
