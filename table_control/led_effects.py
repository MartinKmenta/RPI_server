import threading
import logging
from time import sleep

try:
    from .color_manager import Rgb
    from .led_controller import LedStripsControl
except:
    from color_manager import Rgb
    from led_controller import LedStripsControl


# lock them before using / changing
class LedsEffectSharedVariables():
    def __init__(self):
        logging.debug('LedsEffectSharedVariables - init')
        self.static_effect_waiting_lock = threading.Lock()
        self.data_read_write_lock = threading.Lock()
        self.running_effect = "None"
        self.effect_args = {}
        self.effect_args_changed = False


class LedsEffect(threading.Thread):
    def __init__(self, shared_variables):
        logging.debug('LedsEffect - init')
        threading.Thread.__init__(self)
        self.ledStripsControl = LedStripsControl()
        self.shared_variables = shared_variables
        self.shared_variables.static_effect_waiting_lock.acquire()

        self.effects = {
            "RandomColor" : self.RandomColor,
            "OneColor" : self.OneColor,
            "MoreColors" : self.MoreColors,
            "RandomColorsBlinking" : self.RandomColorsBlinking
        }

        # in ms
        self.delays = {
            "RandomColorsBlinking" : 1000
        }

        self.avaiableEffects = list(self.effects.keys())

        self.UpdateEffectArgs()


    @staticmethod
    def ChangeEffect(shared_variables, effect, effect_args:dict = dict()):
        logging.debug(f'LedsEffect - ChangeEffect - {effect} - {effect_args}')

        logging.debug('LedsEffect - ChangeEffect - data_read_write_lock - lock')
        shared_variables.data_read_write_lock.acquire()
        logging.debug('LedsEffect - ChangeEffect - data_read_write_lock - acquire')
        shared_variables.running_effect = effect
        shared_variables.effect_args = effect_args
        shared_variables.effect_args_changed = True
        shared_variables.data_read_write_lock.release()
        logging.debug('LedsEffect - ChangeEffect - data_read_write_lock - release')

        logging.debug(f'LedsEffect - ChangeEffect - lock')
        shared_variables.static_effect_waiting_lock.release()
        logging.debug(f'LedsEffect - ChangeEffect - release')
        shared_variables.static_effect_waiting_lock.acquire()
        logging.debug(f'LedsEffect - ChangeEffect - acquire')


    @staticmethod
    def StopEffect(shared_variables):
        logging.debug('LedsEffect - StopEffect')
        LedsEffect.ChangeEffect(shared_variables, None)
      

    def UpdateEffectArgs(self):
        logging.debug('LedsEffectsControl - init')
        self.effect_args = self.shared_variables.effect_args

        self.effect_delay = None
        if self.shared_variables.running_effect in self.delays:
            self.effect_delay = self.delays[self.shared_variables.running_effect] / 1000 

        if "speed" in self.effect_args:
            self.effect_delay *= self.effect_args["speed"]

        logging.debug(f'self.effect_delay: {self.effect_delay}')


    def run(self):
        logging.debug('LedsEffect - main')
        while(42):
            logging.debug('LedsEffect - main - tick')

            logging.debug('LedsEffect - main - data_read_write_lock - lock')
            self.shared_variables.data_read_write_lock.acquire()
            logging.debug('LedsEffect - main - data_read_write_lock - acquire')

            if(self.shared_variables.effect_args_changed):
                self.UpdateEffectArgs()
                self.shared_variables.effect_args_changed = False
            effect = self.shared_variables.running_effect

            self.shared_variables.data_read_write_lock.release()
            logging.debug('LedsEffect - main - data_read_write_lock - release')

            if(effect == None or effect not in self.avaiableEffects):
                self.NoEffect()
            else:
                self.effects[effect]()


    def StaticEffectWaitForChange(self):
        logging.debug('LedsEffect StaticEffectWaitForChange - waiting')
        self.shared_variables.static_effect_waiting_lock.acquire()
        logging.debug('LedsEffect StaticEffectWaitForChange - acquire')
        self.shared_variables.static_effect_waiting_lock.release()
        logging.debug('LedsEffect StaticEffectWaitForChange - release')
        logging.debug('LedsEffect StaticEffectWaitForChange - done')


    def Wait(self):
        logging.debug('LedsEffect - wait')
        time_to_wait = self.effect_delay
        logging.debug(f'LedsEffect - waiting {self.effect_delay}')
        sleep(time_to_wait % 1)
        logging.debug(f'sleep(time_to_wait % 1) {time_to_wait % 1}')
        for i in range(int(time_to_wait)):
            if(not self.shared_variables.effect_args_changed):
                sleep(1)
                logging.debug(f'sleep(1)')


    def NoEffect(self):
        logging.debug('LedsEffect NoEffect')
        self.ledStripsControl.CleanUp()
        self.ledStripsControl.Clear()
        self.StaticEffectWaitForChange()


    def RandomColor(self):
        logging.debug('LedsEffect RandomColor')
        self.ledStripsControl.SetAll(Rgb.FromRandom())
        self.StaticEffectWaitForChange()
        

    def OneColor(self):
        logging.debug('LedsEffect OneColor')
        if("color" in self.effect_args):
            self.ledStripsControl.SetAll(self.effect_args["color"])
            self.StaticEffectWaitForChange()
        else:
            logging.error('OneColor - missing color argument for effect')
            self.NoEffect()


    def MoreColors(self):
        logging.debug('LedsEffect UpdateColors')
        if("stripsColors" in self.effect_args):
            self.ledStripsControl.Set(self.effect_args["stripsColors"])
            self.StaticEffectWaitForChange()
        else:
            logging.error('UpdateColors - missing stripsColors argument for effect')
            self.NoEffect()


    # dynamic effects
    def RandomColorsBlinking(self):
        logging.debug('LedsEffect RandomColorsBlinking - blink')
        self.ledStripsControl.SetAll(Rgb.FromRandom())
        self.Wait()


class LedsEffectsControl:
    def __init__(self):
        logging.debug('LedsEffectsControl - init')
        self.shared_variables = LedsEffectSharedVariables()
        self.effect_thread = LedsEffect(self.shared_variables)
        self.avaiableEffects = self.effect_thread.avaiableEffects
        self.avaiableLedStrips = self.effect_thread.ledStripsControl.ledStrips

        self.effect_thread.start()

      
    def StartEffect(self, effect_name, effect_args:dict = dict()):
        logging.debug(f'LedsEffectsControl - StartEffect - {effect_name}, {effect_args}')
        LedsEffect.ChangeEffect(self.shared_variables, effect_name, effect_args)


    def StopEffect(self, locked=False):
        logging.debug(f'LedsEffectsControl - StopEffect')
        LedsEffect.StopEffect(self.shared_variables)


    def GetStatus(self):
        return (self.shared_variables.running_effect, self.shared_variables.effect_args)


    @staticmethod
    def _test_LedsEffectsControl(mode: int = 0):
        def verify():
            while input("Continue?").lower() not in ['','y','yes']:
                print()
                sleep(0.01)
            
        def statusAndVerify():
            print(ledsEffectsControl.GetStatus())
            verify()

        modes = [
                    lambda : sleep(1),
                    verify,
                    statusAndVerify
                ]

        action = modes[mode]    

        ledsEffectsControl = LedsEffectsControl()

        print(f"avaiableEffects: {ledsEffectsControl.avaiableEffects}")
        print(f"avaiableLedStrips: {ledsEffectsControl.avaiableLedStrips}")
        action()
        
        ledsEffectsControl.StartEffect("OneColor", {"color":Rgb.FromColor("cyan")})
        action()

        ledsEffectsControl.StartEffect("MoreColors", 
                {"stripsColors": 
                    { name : Rgb.FromRandom() for name in ledsEffectsControl.avaiableLedStrips}
                }
            )
        action()
        
        ledsEffectsControl.StartEffect("RandomColorsBlinking")
        action()

        ledsEffectsControl.StopEffect()
        action()

        ledsEffectsControl.StartEffect("RandomColorsBlinking")
        action()

        ledsEffectsControl.StartEffect("OneColor", 
            {"color":Rgb().FromColor("red")})
        action()

        ledsEffectsControl.StopEffect()


if __name__ == "__main__":
    # logging.basicConfig(level=logging.ERROR)
    logging.basicConfig(level=logging.DEBUG)
    LedsEffectsControl._test_LedsEffectsControl(2)







































# # lock them before using / changing
# class LedsEffectControlVariables():
#     def __init__(self):
#         self.lock = threading.Lock()
#         self.effect_is_running = False      
#         self.stop_running_effect = False   


# class LedsEffect(threading.Thread):
#     def __init__(self, variables = None, effect_name:str = str(), effect_args: dict = dict()):
#         threading.Thread.__init__(self)
#         self.ledStripsControl = LedStripsControl()
#         self.effect_name = effect_name
#         self.variables = variables
#         self.effect_args = effect_args
#         self.speed = 1 if ("speed" not in effect_args) else effect_args["speed"]
        
#         self.effects = {
#             "CleanUp" : self.CleanUp,
#             "RandomColor" : self.RandomColor,
#             "OneColor" : self.OneColor,
#             "MoreColors" : self.MoreColors,
#             "RandomColorsBlinking" : self.RandomColorsBlinking
#         }
#         self.avaiableEffects = list(self.effects.keys())

#         # in ms
#         self.delays = {
#             "RandomColorsBlinking" : 1000
#         }

      
#     def run(self):
#         if(self.effect_name in self.effects):
#             self.variables.lock.acquire()
#             self.variables.effect_is_running = True
#             self.variables.lock.release()
#             self.effects[self.effect_name]()
#         else:
#             logging.error(f'Leds_effects - unknown effect: {self.effect_name}')


#     def GetDelay(self):
#         if(self.effect_name not in self.delays):
#             return 0
#         return self.speed * (self.delays[self.effect_name] / 1000)


#     def StoppingEffect(self):
#         logging.debug(f'StoppingEffect {self.effect_name}')
#         self.variables.lock.acquire()
#         self.variables.stop_running_effect = False
#         self.variables.effect_is_running = False
#         self.variables.lock.release()


#     def CleanUp(self):
#         logging.debug('CleanUp - done')
#         self.ledStripsControl.CleanUp()
#         self.StoppingEffect()

#     # static effects - don't requires to stop
#     def RandomColor(self):
#         logging.debug('RandomColor - done')
#         self.ledStripsControl.SetAll(Rgb.FromRandom())
#         self.StoppingEffect()
        

#     def OneColor(self):
#         logging.debug('OneColor')
#         if("color" not in self.effect_args):
#             logging.error('OneColor - missing color argument for effect')
#         self.ledStripsControl.SetAll(self.effect_args["color"])
#         self.StoppingEffect()
        

#     def MoreColors(self):
#         logging.debug('UpdateColors')
#         if("stripsColors" not in self.effect_args):
#             logging.error('UpdateColors - missing stripsColors argument for effect')
#         self.ledStripsControl.Set(self.effect_args["stripsColors"])
#         self.StoppingEffect()


#     # dynamic effects
#     def RandomColorsBlinking(self):
#         logging.debug('RandomColorsBlinking')
#         delay = self.GetDelay()
#         while(not self.variables.stop_running_effect):
#             self.ledStripsControl.SetAll(Rgb.FromRandom())
#             sleep(delay)
#         self.StoppingEffect()


# class LedsEffectsControl:
#     def __init__(self):
#         self.variables = LedsEffectControlVariables()
#         self.effect_thread = LedsEffect()
#         self.avaiableEffects = self.effect_thread.avaiableEffects
#         self.avaiableLedStrips = self.effect_thread.ledStripsControl.ledStrips
#         self.lastEffect = { "name" : "NoEffect"}

      
#     def StartEffect(self, effect_name, effect_args:dict = dict()):
#         self.variables.lock.acquire()
#         if(self.variables.effect_is_running):
#             self.StopEffect(locked=True)
#         else:
#             self.variables.lock.release()

#         try:
#             self.effect_thread = LedsEffect(self.variables, effect_name, effect_args=effect_args)
#             self.lastEffect = effect_args
#             self.lastEffect["name"] = effect_name
#             self.variables.lock.acquire()
#             self.effect_is_running = True
#             self.variables.lock.release()
#             logging.debug(f'Leds_effects - starting thread: {effect_name}')
#             self.effect_thread.start()
#         except:
#             logging.error(f'Leds_effects - unable to start thread: {effect_name}')


#     def StopEffect(self, locked=False):
#         self.lastEffect = { "name" : "StopEffect"}
#         if(not locked):
#             self.variables.lock.acquire()
#         if(self.variables.effect_is_running):
#             self.variables.stop_running_effect = True
#         self.variables.lock.release()
#         try:
#             self.effect_thread.join()
#         except:
#             logging.warning('StopEffect - effect_thread ended before join')

#         # leds strips cleanup
#         # static effect - no need to stop it later
#         sleep(0.05)
#         LedsEffect(self.variables, "CleanUp").start()
#         LedsEffect(self.variables, "OneColor", {"color":Rgb()}).start()


#     def GetStatus(self):
#         return self.lastEffect["name"]

#     @staticmethod
#     def _test_LedsEffectsControl(mode: int = 0):
#         def verify():
#             while input("Continue?").lower() not in ['','y','yes']:
#                 print()
#                 sleep(0.01)
            
#         def statusAndVerify():
#             print(ledsEffectsControl.GetStatus())
#             verify()

#         modes = [
#                     lambda : sleep(1),
#                     verify,
#                     statusAndVerify
#                 ]

#         action = modes[mode]    

#         ledsEffectsControl = LedsEffectsControl()

#         # print(f"avaiableEffects: {ledsEffectsControl.avaiableEffects}")
#         # print(f"avaiableLedStrips: {ledsEffectsControl.avaiableLedStrips}")
#         # action()
        
#         # ledsEffectsControl.StartEffect("OneColor", {"color":Rgb.FromColor("cyan")})
#         # action()

#         # ledsEffectsControl.StartEffect("MoreColors", 
#         #         {"stripsColors": 
#         #             { name : Rgb.FromRandom() for name in ledsEffectsControl.avaiableLedStrips}
#         #         }
#         #     )
#         # action()
        
#         # ledsEffectsControl.StartEffect("RandomColorsBlinking")
#         # action()

#         # ledsEffectsControl.StopEffect()
#         # action()

#         ledsEffectsControl.StartEffect("RandomColorsBlinking")
#         action()

#         ledsEffectsControl.StartEffect("OneColor", 
#             {"color":Rgb().FromColor("red")})
#         action()

#         ledsEffectsControl.StopEffect()


# if __name__ == "__main__":
#     # logging.basicConfig(level=logging.ERROR)
#     logging.basicConfig(level=logging.DEBUG)
#     LedsEffectsControl._test_LedsEffectsControl(2)
