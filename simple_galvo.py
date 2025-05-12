import PyDAQmx
import numpy as np
from PyDAQmx import Task



def set_galvos_position(start1, start2):
    """
    Fonction pour envoyer des valeurs à deux galvanomètres en utilisant PyDAQmx.

    :param start1: Valeur pour le Galvo 1 (en Volts).
    :param start2: Valeur pour le Galvo 2 (en Volts).
    """
    try:
        # Créer les tâches pour les deux galvanomètres
        task1 = Task()
        task1.CreateAOVoltageChan("Dev1/ao0", "", start1, start1+0.01, PyDAQmx.DAQmx_Val_Volts, None)

        task2 = Task()
        task2.CreateAOVoltageChan("Dev1/ao1", "", start2, start2+0.01, PyDAQmx.DAQmx_Val_Volts, None)


        data1 = np.array([start1], dtype=np.float64)
        data2 = np.array([start2], dtype=np.float64)


        task1.WriteAnalogF64(1, True, 10.0, PyDAQmx.DAQmx_Val_GroupByChannel, data1, None, None)
        task2.WriteAnalogF64(1, True, 10.0, PyDAQmx.DAQmx_Val_GroupByChannel, data2, None, None)

        # Fermer les tâches après l'écriture
        task1.StopTask()
        task1.ClearTask()
        task2.StopTask()
        task2.ClearTask()

        #print(f"Galvo1 position set to {start1} V, Galvo2 position set to {start2} V.")

    except Exception as e:
        print(f"Error setting galvo positions: {e}")

if __name__=="__main__":
    print("go")
    set_galvos_position(0
                    , 0.0)
