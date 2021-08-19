from time import sleep
import logging
import threading

from color_manager import Rgb
from rpi_hardware import Led_shifter

LEDS_DRIVERS_DATA  = 16
LEDS_DRIVERS_CLOCK = 18

# ! change if HW changes 
# all controled led strips 
# only structure stored in memory... use Leds_control's set/set_all to aply 
class LedStripsControl():
    def __init__(self):
        logging.debug("Led_strips - __init__")
        self.led_shifter = Led_shifter(clock=LEDS_DRIVERS_CLOCK, data=LEDS_DRIVERS_DATA)
        self.default_rgb = Rgb()
        
        self.ledStrips = ["tv","window","monitors","above_table","under_table"]
        self.ledStripsColors = {x : Rgb() for x in self.ledStrips}

    def Set(self, newStripsColors: dict = dict()) -> None:
        """
        Set(self, newStripsColors)
            Return None
        
        Sets led strip colors from dictionary
        """
        logging.debug("Led_strips - Set")
        for strip in newStripsColors:
            if strip in self.ledStripsColors:
                self.ledStripsColors[strip] = newStripsColors[strip]
        self.UpdateLedStrips()

    def SetAll(self, color):
        """
        SetAll(self, color_manager_rgb)
            Return None
            
        Sets each led strip to color then updates
        """
        logging.debug("Led_strips - SetAll")
        for strip in self.ledStripsColors:
            self.ledStripsColors[strip] = color
        self.UpdateLedStrips()

    def Clear(self) -> None:
        """
        Sets all led strips to black 0x000000
        """
        logging.debug("Led_strips - Clear")
        self.SetAll(Rgb())
        self.UpdateLedStrips()

    def Turn_on(self) -> None:
        """
        Sets all led strips to white 0xffffff
        """
        logging.debug("Led_strips - Turn_on")
        self.SetAll(Rgb(255,255,255))
        self.UpdateLedStrips()

    def Get_array(self) -> list:
        """
        Get_array(self)
            Return list of led strip colors
        """
        logging.debug("Led_strips - Get_array")
        # require order [tv, window, monitors, above_table, under_table]
        return list(self.ledStripsColors.values())

    def UpdateLedStrips(self) -> None:
        """
        UpdateLedStrips(self)
            Return None
        
        Updates led strips from ledStripsColors list
        """
        self.led_shifter.Update_leds(self.Get_array())
