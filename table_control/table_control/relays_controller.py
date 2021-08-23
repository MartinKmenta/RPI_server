import logging

try:
    from rpi_hardware import Relays
except ModuleNotFoundError:
    class Relays:
        def Set(self, value):
            pass

    
class RelaysControl:
    """
    A class that interacts with register shifter for relay controll 
    Uses Relays from rpi_hardware
    
    Attributes
    ----------
    relays : rpi_hardware.Relays
        register shifter for relay controll
        
    _avaiableRelays : tuple
        tuple containing names of relays
        
    _relaysNames : dictionary
        keys = avaiableRelays, values = index(avaiableRelays)
        hash map for quick lookup
    """
    def __init__(self):
        logging.debug("RelaysControl - __init__")
        self.relays = Relays()  
        self._avaiableRelays = ("PcSwitch","none_1","PcPower","PcComponentsPower","none_4","none_5","none_6","LedsPower")
        self._relaysStatus = { name : 0 for name in self._avaiableRelays}

    def _update(self) -> None:
        """
        Updates relays from _relaysStatus
        """
        logging.debug(f"RelaysControl - update {self._relaysStatus}")
        
        value = self.ToBin()
        self.relays.Set(value)

    def GetStatus(self) -> dict:
        """
        Return dictionary, keys = _relaysNames, values = bool
        
        bool values represent if relay is on/off
        """
        logging.debug("RelaysControl - GetStatus")
        logging.debug(f"RelaysControl - status is: {self._relaysStatus}")
        return self._relaysStatus.copy()
    
    def FromStatus(self,new_status: dict = dict()) -> None:
        """
        Sets self._relaysStatus to new_status
        """
        logging.debug("RelaysControl - FromStatus")
        for relay in new_status:
            if relay in self._avaiableRelays:
                self._relaysStatus[relay] = new_status[relay]
        self._update()
                
    def FromBin(self,binary_number: int = int()) -> None:
        """
        Sets self._relaysStatus values from binary number
        """
        logging.debug("RelaysControl - FromBin")
        bool_arr = [False] * 8
        
        for i in range(8):
            bool_arr[i] = binary_number & 1
            binary_number = binary_number >> 1
                
        self._relaysStatus = dict(zip(self._avaiableRelays,bool_arr))
        self._update()
    
    def ToBin(self) -> int:
        """
        Converts _relaysStatus to binary number
        """
        logging.debug("RelaysControl - ToBin")
        value = 0x0
        for relay in self._avaiableRelays[::-1]:
            value = (value + self._relaysStatus[relay]) << 1
        value = value >> 1
        logging.debug(f"RelaysControl - binary value is {bin(value)}")
        return value

def _test_relays_controller():
    def await_user_input():
        while input("Continue?").lower() not in ['','y','yes']:
            pass
        
    relay_controller = RelaysControl()
    relay_controller.GetStatus()
    
    logging.debug("Turn on all")
    relay_controller.FromBin(0xff)
    await_user_input()
    
    logging.debug("Turn off all") 
    relay_controller.FromBin(0x00)
    await_user_input()
    
    logging.debug("Turn on individualy")
    x = 0x1
    for _ in range(8):
        relay_controller.FromBin(x)
        x = x << 1
        await_user_input()
        
    logging.debug("Turn on sequentialy")
    x = 0x0
    for _ in range(8):
        x = (x << 1) + 0x1
        relay_controller.FromBin(x)
        await_user_input()
    
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    _test_relays_controller()
