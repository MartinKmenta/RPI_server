from time import sleep

from RPi.GPIO import HIGH, LOW, OUT, IN
import RPi.GPIO as gpio
import random
import psutil
import argparse
import threading
import logging
import json

from led_controller import LedStripsControl
from color_manager import Rgb
from relays_controller import RelaysControl
import led_effects



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
