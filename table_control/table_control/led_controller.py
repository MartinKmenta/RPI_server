from time import sleep
import logging

from color_manager import Rgb

class Led_shifter_debug():
    def Update_leds(self,rgb_arr):
        pass

# try importing rpi_hardware if not defined use dummy debug class
try:
    from rpi_hardware import Led_shifter
except ModuleNotFoundError as ex:
    if __debug__:
        Led_shifter = Led_shifter_debug
    else:
        raise ex


class LedStripsControl():
    def __init__(self):
        logging.debug("Led_strips - __init__")
        self.led_shifter = Led_shifter()
        
        self.ledStrips = ("tv","window","monitors","above_table","under_table")
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

    def SetAll(self, color) -> None:
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


def _test_LedStripsControl(mode: int = 0):
    def verify():
        while input("Continue?").lower() not in ['','y','yes']:
            print()
        
    modes = [
                lambda : sleep(1),
                verify
            ]

    action = modes[mode]    
    
    controller = LedStripsControl()
    
    # Turn_on
    print("Set all to white")
    controller.Turn_on()
    
    # test setting and getting colors
    print("Set led strips to random color")
    for x in range(3):
        new_lscolors = controller.ledStripsColors
        
        for lstrip_key in controller.ledStrips:
            color = Rgb.FromRandom(x)
            new_lscolors[lstrip_key] = color
            print(f"Setting {lstrip_key} to {color}")
            controller.Set(new_lscolors)
            assert controller.ledStripsColors == new_lscolors
            action()
    
    # test set all
    print("Set all to random color")
    for x in range(3):
        color = Rgb.FromRandom(x)
        print(f"setting to {color}")
        controller.SetAll(color)
        action()
    
    print("Set all to black")
    controller.Clear()
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    _test_LedStripsControl(1)
