import time
import logging
from pipython import GCSDevice, PILogger

# Disable pipython logging
PILogger.setLevel(logging.CRITICAL + 1)


class PiController:
    def __init__(self):
        try:
            self.devices = []

            # Primary controller for the daisy chain
            c863 = GCSDevice()
            c863.OpenUSBDaisyChain(description="0185500688")
            daisychain_id = c863.dcid

            # Connect to the first device (already open)
            c863.ConnectDaisyChainDevice(1, daisychain_id)
            self.devices.append(c863)

            # Connect the remaining 3 devices in the chain
            for i in range(2, 5):
                controller = GCSDevice()
                controller.ConnectDaisyChainDevice(i, daisychain_id)
                self.devices.append(controller)

        except Exception as e:
            print(f"[ERROR] Could not connect to daisy chain: {e}")

    def get_pos(self, device_id: int) -> float:
        """
        Returns the position of a given controller.

        Parameters:
        - device_id (int): Index of the controller (1-based).

        Returns:
        - float: Current position on axis 1.
        """
        pos_device = self.devices[device_id - 1].gcscommands.qPOS(1)
        for _, value in pos_device.items():
            return value

    def move_abs(self, controller_id: int, value: float, axe: int = 1) -> None:
        """
        Move a controller to an absolute position.

        Parameters:
        - controller_id (int): Index of the controller (1-based).
        - value (float): Target position.
        - axe (int): Axis to move. Default is 1.
        """
        device = self.devices[controller_id - 1]
        device.gcscommands.MOV(axe, value)
        while not device.gcscommands.qONT(axe)[1]:
            time.sleep(0.005)

    def move_rel(self, controller_id: int, value: float, axe: int = 1) -> None:
        """
        Move a controller by a relative offset.

        Parameters:
        - controller_id (int): Index of the controller (1-based).
        - value (float): Relative movement.
        - axe (int): Axis to move. Default is 1.
        """
        device = self.devices[controller_id - 1]
        device.gcscommands.MVR(axe, value)
        while not device.gcscommands.qONT(axe)[1]:
            time.sleep(0.005)


def search():
    """
    Searches for available USB-connected PI controllers and connects to the selected one.
    """
    with GCSDevice() as pidevice:
        print("Searching for USB-connected PI controllers...")
        devices = pidevice.EnumerateUSB()
        print(devices)
        for i, device in enumerate(devices):
            print(f"{i} - {device}")
        item = int(input("Select the device to connect: "))
        pidevice.ConnectUSB(devices[item])
        print(f"Connected to: {pidevice.qIDN().strip()}")


if __name__ == "__main__":
    pi_controller = PiController()

    print("Current position (controller 4):", pi_controller.get_pos(4))
    pi_controller.move_rel(4, 0.01)
    time.sleep(1)
    print("New position (controller 4):", pi_controller.get_pos(4))
