import time
import logging
from pipython import GCSDevice
from pipython import PILogger

PILogger.setLevel(logging.CRITICAL + 1)


class PiController:

    def __init__(self):
        try:
            self.devices = []
            c863=GCSDevice()
            c863.OpenUSBDaisyChain(description='0185500688')

            daisychainid = c863.dcid
            # print(f"Daisy Chain ID: {daisychainid}")
            c863.ConnectDaisyChainDevice(1, daisychainid)
            self.devices.append(c863)

            c863_2=GCSDevice()
            c863_2.ConnectDaisyChainDevice(2, daisychainid)

            self.devices.append(c863_2)

            c863_3=GCSDevice()
            c863_3.ConnectDaisyChainDevice(3, daisychainid)
            self.devices.append(c863_3)

            c863_4=GCSDevice()
            c863_4.ConnectDaisyChainDevice(4, daisychainid)
            self.devices.append(c863_4)

        except Exception as e:
            print(f"Error occurred while connecting to the daisy chain: {e}")




    def get_pos(self,device_id: int) -> float:

        pos_device = self.devices[device_id-1].gcscommands.qPOS(1)
        for key, value in pos_device.items():
            return value


    def move_abs(self,controller_id: int,value: float,axe=1) -> None:
        self.devices[controller_id-1].gcscommands.MOV(axe,value)
        while not self.devices[controller_id-1].gcscommands.qONT(axe)[1]:
            time.sleep(0.005)


    def move_rel(self,controller_id: int,value: float,axe=1) -> None:
        self.devices[controller_id - 1].gcscommands.MVR(axe, value)
        while not self.devices[controller_id-1].gcscommands.qONT(axe)[1]:
            time.sleep(0.005)






def search():
    """Search controllers on interface, show dialog and connect a controller."""
    with GCSDevice() as pidevice:
        print('search for controllers...')
        #devices = pidevice.EnumerateTCPIPDevices()
        devices = pidevice.EnumerateUSB()
        print(devices)
        for i, device in enumerate(devices):
            print('{} - {}'.format(i, device))
        item = int(input('select device to connect: '))
        #pidevice.ConnectTCPIPByDescription(devices[item])
        pidevice.ConnectUSB(devices[item])
        #print(GCSDevice.GCSDevice)
        print('connected: {}'.format(pidevice.qIDN().strip()))




if __name__=="__main__":
    pi_controller = PiController()
    print(pi_controller.get_pos(4))
    pi_controller.move_rel(4,0.01)
    time.sleep(1)
    print(pi_controller.get_pos(4))


