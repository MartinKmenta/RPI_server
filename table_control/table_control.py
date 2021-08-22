from time import sleep
import logging

from relays_controller import RelaysControl

from color_manager import Rgb
from led_controller import LedStripsControl # todo remove
from led_effects import LedsEffectsControl


if __name__=="__main__":
    logging.basicConfig(
        level=logging.DEBUG
        # level=logging.WARNING
        # level=logging.ERROR
    )

    RelaysControl._test_RelaysControl(0)
    

    relaysControl = RelaysControl()
    ledsEffectsControl = LedsEffectsControl()
    
    print(f"avaiableRelays: {relaysControl.relays}")
    print(f"avaiableEffects: {ledsEffectsControl.avaiableEffects}")
    print(f"avaiableLedStrips: {ledsEffectsControl.avaiableLedStrips}")

    logging.debug(f'end main')  