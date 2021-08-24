from time import sleep
import logging

from .relays_controller import RelaysControl

from .color_manager import Rgb
from .led_effects import LedsEffectsControl


if __name__=="__main__":
    logging.basicConfig(
        level=logging.DEBUG
        # level=logging.WARNING
        # level=logging.ERROR
    )

    RelaysControl._test_RelaysControl(0)
    LedsEffectsControl._test_LedsEffectsControl(0)

    relaysControl = RelaysControl()
    ledsEffectsControl = LedsEffectsControl()

    logging.debug(f'end main')  