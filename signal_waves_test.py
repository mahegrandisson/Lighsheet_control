import numpy as np
import PyDAQmx
from PyDAQmx import *
import keyboard
import time
from scipy import signal as sg
import matplotlib.pyplot as plt

def triangle_signal(amp,freq,duration,sampling_rate):
    time_ = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    sigTri = amp * (2 * np.abs(2 * (np.mod(time_ * freq, 1) - 0.5))) - amp
    plt.plot(time_,sigTri)
    plt.show()
    return sigTri

def step_wave(amp,freq,duration,sampling_rate):

    # Vecteur de temps
    time_ = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

    square_wave = amp * sg.square(2 * np.pi * freq * time_)
    plt.plot(time_,square_wave)
    plt.show()
    return square_wave

# Fonction pour envoyer le signal triangulaire aux galvos
def send_wave_to_galvos(amp, freq, duration, sampling_rate,wave_type="triangle",device="Dev1"):

    if wave_type=="triangle":
        wave = triangle_signal(amp, freq, duration, sampling_rate)
    elif wave_type=="step":
        wave = step_wave(amp, freq, duration, sampling_rate)
    else :
        return "Erreur: nom de wave"

    if -0.05 <= amp <= 0.05:
        task = Task()
        task.CreateAOVoltageChan(f"{device}/ao0", "", -amp, amp, PyDAQmx.DAQmx_Val_Volts, None)
        # Envoyer le signal triangulaire de manière continue
        iter_balayage = 0
        while iter_balayage<10:
            # Écrire le signal triangulaire dans le buffer de la carte DAQ
            start_time = time.time()
            task.WriteAnalogF64(len(wave), True, 10.0, PyDAQmx.DAQmx_Val_GroupByChannel, wave, None,
                                None)
            end_time=time.time()
            print("T_exec=",end_time-start_time)
            iter_balayage+=1
            # Attendre avant de répéter l'envoi du signal
            time.sleep(duration)

        # Nettoyer la tâche
        task.StopTask()
        task.ClearTask()



if __name__ == "__main__":
    freq = 50
    duration = 1
    sampling_rate = 1000
    amp = 0.05
    transition_time =0.5

    send_wave_to_galvos(amp,freq, duration, sampling_rate,wave_type="step")


