import threading
import logging
from time import sleep

from color_manager import Rgb
from led_controller import LedStripsControl

# lock them before using / changing
class LedsEffectControlVariables():
    def __init__(self):
        self.lock = threading.Lock()
        self.effect_is_running = False      
        self.stop_running_effect = False   


class LedsEffect(threading.Thread):
    def __init__(self, variables = None, effect_name:str = str(), effect_args: dict = dict()):
        threading.Thread.__init__(self)
        self.ledStripsControl = LedStripsControl()
        self.effect_name = effect_name
        self.variables = variables
        self.effect_args = effect_args
        self.speed = 1 if ("speed" not in effect_args) else effect_args["speed"]
        
        self.effects = {
            "RandomColor" : self.RandomColor,
            "OneColor" : self.OneColor,
            "MoreColors" : self.MoreColors,
            "RandomColorsBlinking" : self.RandomColorsBlinking
        }
        self.avaiableEffects = list(self.effects.keys())

        # in ms
        self.delays = {
            "RandomColorsBlinking" : 1000
        }

      
    def run(self):
        if(self.effect_name in self.effects):
            self.variables.lock.acquire()
            self.variables.effect_is_running = True
            self.variables.lock.release()
            self.effects[self.effect_name]()
        else:
            logging.error(f'Leds_effects - unknown effect: {self.effect_name}')


    def GetDelay(self):
        if(self.effect_name not in self.delays):
            return 0
        return self.speed * (self.delays[self.effect_name] / 1000)


    def StoppingEffect(self):
        logging.debug(f'StoppingEffect {self.effect_name}')
        self.variables.lock.acquire()
        self.variables.stop_running_effect = False
        self.variables.effect_is_running = False
        self.variables.lock.release()


    # static effects - requres to stop
    def RandomColor(self):
        logging.debug('RandomColor - done')
        self.ledStripsControl.SetAll(Rgb.FromRandom())
        self.StoppingEffect()
        

    def OneColor(self):
        logging.debug('OneColor')
        if("color" not in self.effect_args):
            logging.error('OneColor - missing color argument for effect')
        self.ledStripsControl.SetAll(self.effect_args["color"])
        self.StoppingEffect()
        

    def MoreColors(self):
        logging.debug('UpdateColors')
        if("stripsColors" not in self.effect_args):
            logging.error('UpdateColors - missing stripsColors argument for effect')
        self.ledStripsControl.Set(self.effect_args["stripsColors"])
        self.StoppingEffect()


    # dynamic effects
    def RandomColorsBlinking(self):
        logging.debug('RandomColorsBlinking')
        delay = self.GetDelay()
        while(not self.variables.stop_running_effect):
            self.ledStripsControl.SetAll(Rgb.FromRandom())
            sleep(delay)
        self.StoppingEffect()


class LedsEffectsControl:
    def __init__(self):
        self.variables = LedsEffectControlVariables()
        self.effect_thread = LedsEffect()
        self.avaiableEffects = self.effect_thread.avaiableEffects
        self.avaiableLedStrips = self.effect_thread.ledStripsControl.ledStrips
        self.lastEffect = { "name" : "NoEffect"}

      
    def StartEffect(self, effect_name, effect_args:dict = dict()):
        self.variables.lock.acquire()
        if(self.variables.effect_is_running):
            self.StopEffect(locked=True)
        else:
            self.variables.lock.release()

        try:
            self.effect_thread = LedsEffect(self.variables, effect_name, effect_args=effect_args)
            self.lastEffect = effect_args
            self.lastEffect["name"] = effect_name
            self.variables.lock.acquire()
            self.effect_is_running = True
            self.variables.lock.release()
            logging.debug(f'Leds_effects - starting thread: {effect_name}')
            self.effect_thread.start()
        except:
            logging.error(f'Leds_effects - unable to start thread: {effect_name}')


    def StopEffect(self, locked=False):
        self.lastEffect = { "name" : "StopEffect"}
        if(not locked):
            self.variables.lock.acquire()
        if(self.variables.effect_is_running):
            self.variables.stop_running_effect = True
        self.variables.lock.release()
        try:
            self.effect_thread.join()
        except:
            logging.warning('StopEffect - effect_thread ended before join')

        # leds strips cleanu
        # static effect - no need to stop it later
        sleep(0.01)
        LedsEffect(self.variables, "OneColor", {"color":Rgb()}).start()


    def GetStatus(self):
        return self.lastEffect["name"]
