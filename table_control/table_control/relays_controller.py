import logging
from rpi_hardware import Relays

class RelaysControl:
    def __init__(self):
        logging.debug("RelaysControl - __init__")
        self.relays = Relays()  
        self.relaysValue = 0
        self.avaiableRelays = ("PcSwitch","none_1","PcPower","PcComponentsPower","none_4","none_5","none_6","LedsPower")
        self.relaysNames = { name : i for i,name in enumerate(self.avaiableRelays)}

        # todo uncoment
        # self.TurnOfAll()

    def SetAll(self, value):
        logging.debug(f"RelaysControl - SetAll {bin(value)}")
        self.relaysValue = value
        self.relays.Set(value)

    def SetSome(self, values):
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
        logging.debug("RelaysControl - StartPc")
        value = self.relaysValue
        # todo 
        self.relays.Set(value)

    def TurnOfAll(self):
        logging.debug("RelaysControl - TurnOfAll")
        self.relaysValue = 0x00
        self.relays.Stop()

    def GetStatus(self):
        logging.debug("RelaysControl - GetStatus")
        relaysStatus = {}
        for relay in self.relaysNames:
            relaysStatus[relay] = (self.relaysValue >> self.relaysNames[relay]) & 1 == 1
        logging.debug(f"RelaysControl - status is: {relaysStatus}")
        return relaysStatus
