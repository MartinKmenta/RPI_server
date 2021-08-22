from time import sleep
import logging

try:
    from rpi_hardware import Relays
except ModuleNotFoundError:
    class Relays:
        def Set(self, value):
            print(f"Relays: {bin(value)}")
        
        def Stop(self):
            print("Relays: Stop()")
    
class RelaysControl:
    def __init__(self):
        logging.debug("RelaysControl - __init__")
        self.relays_shifter = Relays()  

        self.relays = ("PcSwitch","none_1","PcPower","PcComponentsPower","none_4","none_5","none_6","LedsPower")
        self.relaysValue = { name : 0 for i,name in enumerate(self.relays)}

        # todo uncoment
        # self.TurnOfAll()

    def SetSome(self, values) -> None:
        """
        values is a list of 8-bit numbers, calls Relays.Set from rpi_hardware
        """
        logging.debug(f"RelaysControl - SetSome {values}")
        value = self.relaysValue
        for relayName in values:
            if relayName in self.relays:
                self.relaysValue[relayName] = values[relayName]
            else:
                logging.error(f"RelaysControl - SetSome ERROR - value: {relayName} is not in relaysNames")

        self.UpdateRelays()

    def StartPc(self):
        logging.debug("RelaysControl - StartPc")
        self.relaysValue["PcPower"] = 1
        self.UpdateRelays()
        sleep(1)
        self.relaysValue["PcSwitch"] = 1
        self.UpdateRelays()
        sleep(1)
        self.relaysValue["PcSwitch"] = 0
        self.UpdateRelays()

    def TurnOffPc(self):
        logging.debug("RelaysControl - TurnOffPc")
        self.relaysValue["PcPower"] = 0
        self.relaysValue["PcComponentsPower"] = 0
        self.UpdateRelays()

    def TurnOnPcComponents(self):
        logging.debug("RelaysControl - TurnOnPcComponents")
        self.relaysValue["PcComponentsPower"] = 1
        self.UpdateRelays()

    def TurnOffPcComponents(self):
        logging.debug("RelaysControl - TurnOffPcComponents")
        self.relaysValue["PcComponentsPower"] = 0
        self.UpdateRelays()

    def TurnOnLeds(self):
        logging.debug("RelaysControl - TurnOnLeds")
        self.relaysValue["LedsPower"] = 1
        self.UpdateRelays()

    def TurnOffLeds(self):
        logging.debug("RelaysControl - TurnOffLeds")
        self.relaysValue["LedsPower"] = 0
        self.UpdateRelays()

    def TurnOfAll(self) -> None:
        # """
        # Sets relaysValue to 0 for all elements in dict and calls Relays.Stop() from rpi_hardware
        # """
        # logging.debug("RelaysControl - TurnOfAll")
        # self.relaysValue = { relaysValue[name] = 0 for name in relaysValue}
        # self.relays.Stop()
        """
        Call SetFromValue with 0x00 to turn off all relays 
        (possibility to use self.relays_shifter.Stop())
        """
        logging.debug("RelaysControl - TurnOfAll")
        self.SetFromValue(0x00)

    def GetStatus(self) -> dict:
        """
        Return dictionary, keys = self.relaysNames, values = int
        """
        logging.debug(f"RelaysControl - GetStatus - status is: {self.relaysValue}")
        return self.relaysValue

    def SetFromValue(self, value = 0x00) -> None:
        """
        Set registe values from 8 bit number representing relays values
        """
        logging.debug(f"RelaysControl - SetFromValue: {bin(value)}")
        for i,relayName in enumerate(self.relays):
            self.relaysValue[relayName] = value >> (7 - i) & 1
        self.UpdateRelays()

    def Get_value(self) -> int:
        """
        Return one 8 bit number representing relays values
        """
        logging.debug("RelaysControl - Get_value")
        relaysVal = 0
        for i,val in enumerate(self.relaysValue.values()):
            relaysVal += val << (7 - i)
        return relaysVal

    def UpdateRelays(self) -> None:
        """
        Updates relays from relaysValue
        """
        logging.debug("RelaysControl - UpdateRelays")
        self.relays_shifter.Set(self.Get_value())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)