import time
import logging
from pipython import (
    GCSDevice,
    PILogger,
)

# Supprimer les logs de pipython
PILogger.setLevel(logging.CRITICAL + 1)


class PiController:
    def __init__(
        self,
    ):
        try:
            self.devices = []

            # Premier contrôleur principal pour la chaîne daisy
            c863 = GCSDevice()
            c863.OpenUSBDaisyChain(description="0185500688")
            daisychain_id = c863.dcid

            # Connexion au premier appareil (déjà ouvert)
            c863.ConnectDaisyChainDevice(
                1,
                daisychain_id,
            )
            self.devices.append(c863)

            # Connexion aux 3 autres appareils de la chaîne
            for i in range(
                2,
                5,
            ):
                controller = GCSDevice()
                controller.ConnectDaisyChainDevice(
                    i,
                    daisychain_id,
                )
                self.devices.append(controller)

        except Exception as e:
            print(f"[ERREUR] Impossible de se connecter à la chaîne daisy : {e}")

    def get_pos(
        self,
        device_id: int,
    ) -> float:

        pos_device = self.devices[device_id - 1].gcscommands.qPOS(1)
        for (
            _,
            value,
        ) in pos_device.items():
            return value

    def move_abs(
        self,
        controller_id: int,
        value: float,
        axe: int = 1,
    ) -> None:

        device = self.devices[controller_id - 1]
        device.gcscommands.MOV(
            axe,
            value,
        )
        while not device.gcscommands.qONT(axe)[1]:
            time.sleep(0.005)

    def move_rel(
        self,
        controller_id: int,
        value: float,
        axe: int = 1,
    ) -> None:

        device = self.devices[controller_id - 1]
        device.gcscommands.MVR(
            axe,
            value,
        )
        while not device.gcscommands.qONT(axe)[1]:
            time.sleep(0.005)


def search():
    with GCSDevice() as pidevice:
        print("Recherche de contrôleurs PI connectés en USB...")
        devices = pidevice.EnumerateUSB()
        print(devices)
        for (
            i,
            device,
        ) in enumerate(devices):
            print(f"{i} - {device}")
        item = int(input("Sélectionner l'appareil à connecter : "))
        pidevice.ConnectUSB(devices[item])
        print(f"Connecté à : {pidevice.qIDN().strip()}")


if __name__ == "__main__":
    pi_controller = PiController()

    print(
        "Position actuelle (contrôleur 4) :",
        pi_controller.get_pos(4),
    )
    pi_controller.move_rel(
        4,
        0.01,
    )
    time.sleep(1)
    print(
        "Nouvelle position (contrôleur 4) :",
        pi_controller.get_pos(4),
    )
