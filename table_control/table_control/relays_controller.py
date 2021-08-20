import logging

try:
    from rpi_hardware import Relays
except ModuleNotFoundError:
    class Relays:
        def Set(self, value):
            pass
        
        def Stop(self):
            pass
    
class RelaysControl:
    """
    A class that interacts with register shifter for relay controll 
    Uses Relays from rpi_hardware
    
    Attributes
    ----------
    relays : rpi_hardware.Relays
        register shifter for relay controll
    
    relaysValue : int
        binary number, representing array of bools
        
    avaiableRelays : tuple
        tuple containing names of relays
        
    relaysNames : dictionary
        keys = avaiableRelays, values = index(avaiableRelays)
        hash map for quick lookup
    
    """
    def __init__(self):
        logging.debug("RelaysControl - __init__")
        self.relays = Relays()  
        self.relaysValue = 0
        self.avaiableRelays = ("PcSwitch","none_1","PcPower","PcComponentsPower","none_4","none_5","none_6","LedsPower")
        self.relaysNames = { name : i for i,name in enumerate(self.avaiableRelays)}

        # todo uncoment
        # self.TurnOfAll()

    def SetAll(self, value) -> None:
        """
        Sets relays according to 8 bit number
        """
        logging.debug(f"RelaysControl - SetAll {bin(value)}")
        self.relaysValue = value
        self.relays.Set(value)

    def SetSome(self, values) -> None:
        """
        values is a list of 8-bit numbers, calls Relays.Set from rpi_hardware
        """
        logging.debug(f"RelaysControl - SetSome {values}")
        value = self.relaysValue
        for val in values:
            if val in self.relaysNames:
                value ^= ((value >> self.relaysNames[val] & 1) ^ values[val]) << self.relaysNames[val]
            else:
                logging.error(f"RelaysControl - SetSome ERROR - value: {val} is not in relaysNames")

        self.relaysValue = value
        self.relays.Set(value)

    def StartPc(self):
        """
        sequence of operations that safely poweres PC
        """
        logging.debug("RelaysControl - StartPc")
        value = self.relaysValue
        # todo 
        self.relays.Set(value)

    def TurnOfAll(self) -> None:
        """
        Sets relaysValue to 0x00 (base-16) and calls Relays.Stop() from rpi_hardware
        """
        logging.debug("RelaysControl - TurnOfAll")
        self.relaysValue = 0x00
        self.relays.Stop()

    def GetStatus(self) -> dict:
        """
        Return dictionary, keys = relaysNames, values = bool
        
        Converts relaysValue (8-bit) to dictonary, keys = relaysNames and values = bool representing if relay works
        """
        logging.debug("RelaysControl - GetStatus")
        relaysStatus = dict()
        for relay in self.relaysNames:
            relaysStatus[relay] = (self.relaysValue >> self.relaysNames[relay]) & 1 == 1
        logging.debug(f"RelaysControl - status is: {relaysStatus}")
        return relaysStatus

def _test_relays_controller():
    def await_user_input():
        while input("Continue?").lower() not in ['','y','yes']:
            pass
        
    relay_controller = RelaysControl()
    relay_controller.GetStatus()
    
    logging.debug("Turn on all")
    relay_controller.SetAll(0b11111111)
    relay_controller.GetStatus()
    await_user_input()
    
    logging.debug("Turn off all") 
    relay_controller.TurnOfAll()
    relay_controller.GetStatus()
    await_user_input()
    
    logging.debug("Turn on individualy")
    x = 0x1
    relay_controller.SetAll(x)
    await_user_input()
    
    for _ in range(7):
        x = x << 1
        relay_controller.SetAll(x)
        await_user_input()
        
    logging.debug("Turn on sequentialy")
    x = 0x0
    for _ in range(8):
        x = (x << 1) + 0x1
        relay_controller.SetAll(x)
        await_user_input()
    
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    _test_relays_controller()
