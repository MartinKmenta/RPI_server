from time import sleep

from RPi.GPIO import HIGH, LOW, OUT, IN
import RPi.GPIO as gpio
import random
import psutil
import argparse
import threading
import logging
import json


LEDS_DRIVERS_DATA  = 16
LEDS_DRIVERS_CLOCK = 18

RELAYS_DATA   =  8
RELAYS_LATCH  = 10
RELAYS_CLOCK  = 12
RELAYS_PAUSE  = 0.03


# for controling shift registers
class Shifter():
    def __init__(self, clock, data, latch, pause):
        logging.debug("Shifter - __init__")
        self.clock_pin = clock
        self.data_pin  = data
        self.latch_pin = latch
        self.pause     = pause
        self.Setup_board()

    def Tick(self):
        # logging.debug("Shifter - Tick")
        sleep(self.pause)
        gpio.output(self.clock_pin, LOW)
        sleep(self.pause)
        gpio.output(self.clock_pin, HIGH)
        sleep(self.pause)

    def Update(self):
        logging.debug("Shifter - Update")
        gpio.output(self.latch_pin, LOW)
        sleep(self.pause)
        gpio.output(self.latch_pin, HIGH)
        sleep(self.pause)
        gpio.output(self.latch_pin, LOW)
        sleep(self.pause)

    def Set_value_1_bit(self, value):
        logging.debug("Shifter - Set_value_1_bit")
        logging.debug("shifting: " + str(value))
        if value:
            gpio.output(self.data_pin, HIGH)
        else:
            gpio.output(self.data_pin, LOW)
        self.Tick()
        self.Update()

    def Set_value_8_bit(self, value):
        logging.debug("Shifter - Set_value_8_bit")
        logging.debug("Set_value_8_bit: " + str(bin(value)))
        gpio.output(self.data_pin, HIGH)
        for i in range(8):
            if value & 0x80 >> i:
                gpio.output(self.data_pin, HIGH)
            else:
                gpio.output(self.data_pin, LOW)
            self.Tick()
        self.Update()

    def Set_value_8_bit_inv(self, value):
        logging.debug("Shifter - Set_value_8_bit_inv")
        self.Set_value_8_bit(value ^ 0xFF)

    def Setup_board(self):
        logging.debug("Shifter - Setup_board")
        gpio.setmode(gpio.BOARD)
        gpio.setup (self.clock_pin, OUT)
        gpio.output(self.clock_pin, LOW)
        gpio.setup (self.data_pin,  OUT)
        gpio.output(self.data_pin,  LOW)
        gpio.setup (self.latch_pin, OUT)
        gpio.output(self.latch_pin, LOW)
        

# for controling relays in table
class Relays():
    def __init__(self):
        logging.debug("Relays - __init__")
        self.shifter = Shifter(clock=RELAYS_CLOCK, data=RELAYS_DATA, 
            latch=RELAYS_LATCH, pause=RELAYS_PAUSE)

    def Set(self, value):
        logging.debug(f"Relays - Set {bin(value)}")
        self.shifter.Set_value_8_bit_inv(value)

    def Shift(self, value):
        logging.debug(f"Relays - Shift {bin(value)}")
        self.shifter.Set_value_1_bit(value ^ 1)

    def Stop(self):
        logging.debug("Relays - Stop")
        self.shifter.Set_value_8_bit_inv(0x00)


class RelaysControl:
    def __init__(self):
        logging.debug("RelaysControl - __init__")
        self.relays = Relays()  
        self.relaysValue = 0
        self.relaysNames = {
            "PcSwitch" : 0,
            "none_1" : 1,
            "PcPower" : 2,
            "PcComponentsPower" : 3,
            "none_4" : 4,
            "none_5" : 5,
            "none_6" : 6,
            "LedsPower" : 7,
        }
        self.avaiableRelays = list(self.relaysNames.keys())

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


# color object
class Rgb():
    def __init__(self, r = 0, g = 0, b = 0):
        self.r = self.Set(r)
        self.g = self.Set(g)
        self.b = self.Set(b)
        
        # todo add more
        self.colors = {
            "random"    : {"r":random.randint(0, 256), "g":random.randint(0, 256), "b":random.randint(0, 256)},
            "default"   : {"r":  0, "g":  0, "b":  0},

            "white"     : {"r":255, "g":255, "b":255},
            "red"       : {"r":255, "g":  0, "b":  0},
            "green"     : {"r":  0, "g":255, "b":  0},
            "blue"      : {"r":  0, "g":  0, "b":255},
            "cyan"      : {"r":  0, "g":255, "b":255},
            "magenta"   : {"r":255, "g":  0, "b":255},
            "yellow"    : {"r":255, "g":255, "b":  0},
            "black"     : {"r":  0, "g":  0, "b":  0}
        }


    def GetColor(self, color):
        color = color.lower()
        if(color in self.colors):
            c = self.colors[color]
            self.r = c["r"]
            self.g = c["g"]
            self.b = c["b"]
            return self 
        else:
            logging.error("Rgb ERROR - unknown color: {color}")


    # accepts string in formats: #000000, 0x000000
    def FromHex(self, color):
        logging.debug(f'Rgb - FromHex: {color}')
        try:
            if "#" in color:
                color = color.replace("#", "0x")
            colorHex = int(color, base=16)
            self.r = (colorHex & 0xff0000) >> 16
            self.g = (colorHex & 0xff00) >> 8
            self.b = colorHex & 0xff
            return self 
        except:
            logging.error(f'Rgb - FromHex - unable to decode color: {color}')
        
        return self.GetColor("default")

    def Set(self, val):
        return 255 if val > 255 else 0 if val < 0 else int(val)

    # def Random(self):   return Rgb(random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))
    # def White(self):    return Rgb(255, 255, 255)
    # def Red(self):      return Rgb(255,   0,   0)
    # def Green(self):    return Rgb(  0, 255,   0)
    # def Blue(self):     return Rgb(  0,   0, 255)
    # def Cyan(self):     return Rgb(  0, 255, 255)
    # def Magenta(self):  return Rgb(255,   0, 255)
    # def Yellow(self):   return Rgb(255, 255,   0)
    # def Black(self):    return Rgb(  0,   0,   0)


# for shifting led strips
class Led_shifter():
    def __init__(self, clock, data):
        logging.debug("Led_shifter - __init__")
        self.pause     = 0
        self.data_pin  = data
        self.clock_pin = clock
        self.Setup_board()

    def Tick(self):
        # logging.debug("Led_shifter - Tick")
        gpio.output(self.clock_pin, LOW)
        sleep(self.pause)
        gpio.output(self.clock_pin, HIGH)
        sleep(self.pause)

    def Send_32_zero(self):
        logging.debug("Led_shifter - Send_32_zero")
        for i in range(32):
            gpio.output(self.data_pin, LOW)
            self.Tick()

    def Get_anti_code(self, data):
        # logging.debug("Led_shifter - Get_anti_code")
        return (data >> 6) & 0x03

    def Send_data(self, data):
        logging.debug("Led_shifter - Send_data")
        logging.debug(data)
        for i in range(32):
            if data & 0x80000000:
                gpio.output(self.data_pin, HIGH)
            else:
                gpio.output(self.data_pin, LOW)
            data <<= 1
            self.Tick()

    def Update_1_led_strip(self, rgb):
        logging.debug("Led_shifter - Update_1_led_strip")
        logging.debug(str(rgb.r) + " " + str(rgb.g) + " " + str(rgb.b))
        data = 0x03 << 30
        data |= self.Get_anti_code(rgb.b) << 28
        data |= self.Get_anti_code(rgb.g) << 26
        data |= self.Get_anti_code(rgb.r) << 24
        data |= rgb.b << 16
        data |= rgb.g << 8
        data |= rgb.r
        self.Send_data(data)

    def Update_leds(self, rgb_arr):
        logging.debug("Led_shifter - Update_leds")
        self.Send_32_zero()
        for rgb in rgb_arr:
            logging.debug(str(rgb.r) + " " + str(rgb.g) + " " + str(rgb.b))
            self.Update_1_led_strip(rgb)
        self.Send_32_zero()

    def Setup_board(self):
        logging.debug("Led_shifter - Setup_board")
        gpio.setmode(gpio.BOARD)
        gpio.setup(self.data_pin,    OUT)
        gpio.output(self.data_pin,   LOW)
        gpio.setup(self.clock_pin,   OUT)
        gpio.output(self.clock_pin,  LOW)


# ! change if HW changes 
# all controled led strips 
# only structure stored in memory... use Leds_control's set/set_all to aply 
class LedStripsControl():
    def __init__(self):
        logging.debug("Led_strips - __init__")
        self.led_shifter = Led_shifter(clock=LEDS_DRIVERS_CLOCK, data=LEDS_DRIVERS_DATA)
        self.default_rgb = Rgb().GetColor("black")
        
        self.ledStripsColors = {
            "tv" : self.default_rgb,
            "window" : self.default_rgb,
            "monitors" : self.default_rgb,
            "above_table" : self.default_rgb,
            "under_table" : self.default_rgb
        }
        self.ledStrips = list(self.ledStripsColors.keys())

    def Set(self, newStripsColors):
        logging.debug("Led_strips - Set")
        for strip in newStripsColors:
            if strip in self.ledStripsColors:
                self.ledStripsColors[strip] = newStripsColors[strip]
        self.UpdateLedStrips()

    def SetAll(self, color):
        logging.debug("Led_strips - SetAll")
        for strip in self.ledStripsColors:
            self.ledStripsColors[strip] = color
        self.UpdateLedStrips()

    def Clear(self):
        logging.debug("Led_strips - Clear")
        self.SetAll(Rgb().Black())
        self.UpdateLedStrips()

    def Turn_on(self):
        logging.debug("Led_strips - Turn_on")
        self.SetAll(Rgb().White())
        self.UpdateLedStrips()

    def Get_array(self):
        logging.debug("Led_strips - Get_array")
        # require order [tv, window, monitors, above_table, under_table]
        return list(self.ledStripsColors.values())

    def UpdateLedStrips(self):
       self.led_shifter.Update_leds(self.Get_array())


# lock them before using / changing
class LedsEffectControlVariables():
    def __init__(self):
        self.lock = threading.Lock()
        self.effect_is_running = False      
        self.stop_running_effect = False   


class LedsEffect(threading.Thread):
    def __init__(self, variables=None, effect_name="", effect_args={}):
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
        logging.debug(f'RandomColor - done')
        self.ledStripsControl.SetAll(Rgb().GetColor("random"))
        self.StoppingEffect()
        

    def OneColor(self):
        logging.debug(f'OneColor')
        if("color" not in self.effect_args):
            logging.error(f'OneColor - missing color argument for effect')
        self.ledStripsControl.SetAll(self.effect_args["color"])
        self.StoppingEffect()
        

    def MoreColors(self):
        logging.debug(f'UpdateColors')
        if("stripsColors" not in self.effect_args):
            logging.error(f'UpdateColors - missing stripsColors argument for effect')
        self.ledStripsControl.Set(self.effect_args["stripsColors"])
        self.StoppingEffect()


    # dynamic effects
    def RandomColorsBlinking(self):
        logging.debug(f'RandomColorsBlinking')
        delay = self.GetDelay()
        while(not self.variables.stop_running_effect):
            self.ledStripsControl.SetAll(Rgb().GetColor("random"))
            sleep(delay)
        self.StoppingEffect()


class LedsEffectsControl:
    def __init__(self):
        self.variables = LedsEffectControlVariables()
        self.effect_thread = LedsEffect()
        self.avaiableEffects = self.effect_thread.avaiableEffects
        self.avaiableLedStrips = self.effect_thread.ledStripsControl.ledStrips
        self.lastEffect = { "name" : "NoEffect"}

      
    def StartEffect(self, effect_name, effect_args={}):
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
            logging.warning(f'StopEffect - effect_thread ended before join')

        # leds strips cleanu
        # static effect - no need to stop it later
        sleep(0.01)
        LedsEffect(self.variables, "OneColor", {"color":Rgb().GetColor("default")}).start()


    def GetStatus(self):
        return self.lastEffect["name"]


if __name__=="__main__":
    
    logging.basicConfig(
        level=logging.DEBUG
        # level=logging.WARNING
        # level=logging.ERROR
    )


    
    relaysControl = RelaysControl()
    logging.warning("avaiableRelays")
    logging.warning(relaysControl.avaiableRelays)
    
            # "PcSwitch" : 0,
            # "none_1" : 1,
            # "PcPower" : 2,
            # "PcComponentsPower" : 3,
            # "none_4" : 4,
            # "none_5" : 5,
            # "none_6" : 6,
            # "LedsPower" : 7,

    sleep(0.3)
    relaysControl.SetSome({
        "PcSwitch" : 1,
        "PcPower" : 1,
        "PcComponentsPower" : 1,
        "LedsPower" : 0
    })
    # relaysControl.TurnOfAll()
        
        # relaysControl.SetSome({
        #     "PcSwitch" : 1,
        #     "PcPower" : 1,
        #     "PcComponentsPower" : 1,
        #     "LedsPower" : 0
        # })
        # sleep(5)
        # relaysControl.TurnOfAll()
        # sleep(5)


    # ledsEffectsControl = LedsEffectsControl()

    # logging.warning("avaiableEffects")
    # logging.warning(ledsEffectsControl.avaiableEffects)
    # logging.warning("avaiableEffects")
    # logging.warning(ledsEffectsControl.avaiableLedStrips)


    # ledsEffectsControl.StartEffect("MoreColors", 
    #     {"stripsColors": { "under_table":Rgb().GetColor("random")}})

    # ledsEffectsControl.StopEffect()

    # ledsEffectsControl.StartEffect("OneColor", 
    #     {"color":Rgb().GetColor("cyan")})

    # sleep(0.5)

    # ledsEffectsControl.StopEffect()


    logging.debug(f'end main')  




        # cnt = cnt + 1
        # if (blue == 80) | (blue == 10) :
        #     add = add * (-1)
        # if (cnt < 1000) :
        #     leds.Update_leds((  Rgb(255, 255, blue) ,  Rgb(255, 255, blue)  ,  Rgb(255, 255, blue)  ,  Rgb(255, 255, blue)  ,  Rgb(255, 255, blue)  ))
        # else:
        #         leds.Update_leds((  Rgb(255, blue, 255) ,  Rgb(255, blue, 255)  ,  Rgb(255, blue, 255)  ,  Rgb(255, blue, 255)  ,  Rgb(255, blue, 255)  ))
        # blue = blue + add
        # cnt = cnt % 2000
        # sleep(0.05)

        # re = r()
        # g = r()
        # b = r()

        # leds.Update_leds((  Rgb(re, g, b) ,  Rgb(b, g, re)  ,  Rgb(re, g, b)  ,  Rgb(b, g, re)  ,  Rgb(re, g, b)  ))

        # sleep(0.055)

# def CheckMyInstances():



# if __name__=="__main__":
#     parser = argparse.ArgumentParser(description='Table control')
#     parser.add_argument("-r", type=int, dest="red", help="")
#     parser.add_argument("-g", type=int, dest="green", help="")
#     parser.add_argument("-b", type=int, dest="blue", help='')
            
#     args = parser.parse_args()


    # leds = Leds_control()
    

    # leds.led_strips.SetAll(Rgb(args.red, args.green, args.blue))
    # # leds.led_strips.Clear()
    # leds.Set()






    # try: args = parser.parse_args()
    # except SystemExit as e:
    #     exit(NO_ERROR if str(e) == "0" else ERROR_MISSING_OR_WRONG_PARAMETER)

    # if args.inp == None and args.src == None:
    #     exit(ERROR_MISSING_OR_WRONG_PARAMETER)

    # statistics = None
    # if args.file_for_statistics != None:
    #     statistics = Statistics(args.file_for_statistics)
    #     statistics.SeparateStatsArguments(args, sys.argv)

    # PROCNAME = "python.exe"
    # for proc in psutil.process_iter():
    #     # check whether the process name matches
    #     # if proc.name() == PROCNAME:
    #     #     proc.kill()
    #     print(proc.name())
    # exit(0)

    # leds = Leds_control()

    # running = True

    

    # relays.Set(0x00)
    # sleep(2)












    # relays = Relays()
    # relays.Set(0xFF)

    # relays.Stop()
    # sleep(2)
    # # logging.debug("0x01")
    # # relays.Set(0x01)
    # sleep(2)
    # relays.Set(0x02)
    # # sleep(2)
    # # logging.debug("0xFF")
    # # relays.Set(0xFF)

    # sleep(2)
    # relays.Stop()
    # logging.debug("stop")

    # sleep(2)
    # logging.debug("cleaneup")
    # logging.debug()
    # gpio.cleanup()
    # exit(0)

    # leds.Update_leds([c["white"], c["white"], c["white"]])
    # leds.Update_leds([c["black"], c["black"], c["black"]])
    # # sleep(3)
    # relays.Set(0x01)
    # sleep(3)

    # exit(0)

    # sleep(2)
    # blue = 50
    # add = 1
    # cnt = 0



    # while running == True:
    #     try:


    #         relays.Set(0x01)

    #         for i in range(8):
    #             sleep(1)
    #             # relays.Shift(0)
    #             # relays.Stop()
    #             relays.Shift(0)
    #             # relays.Shift(1)
    #             # relays.Shift(1)
    #             # relays.Set(0xFF)

    #         sleep(1)




    #     except KeyboardInterrupt:
    #         running = False
    #         print()
    #         print("cleaneup")
    #         print()
    #         gpio.cleanup()



#  sudo python3 table_control.py



    # gpio.cleanup()
