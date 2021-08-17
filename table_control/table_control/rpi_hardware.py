import logging
from time import sleep

from RPi.GPIO import HIGH, LOW, OUT, IN
import RPi.GPIO as gpio

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
    """
    Relays
    """
    
    def __init__(self):
        """
        Creates instance of Shifter with Relays parameters
        """
        
        logging.debug("Relays - __init__")
        self.shifter = Shifter(clock = RELAYS_CLOCK,
                               data  = RELAYS_DATA, 
                               latch = RELAYS_LATCH, 
                               pause = RELAYS_PAUSE)

    def Set(self, value):
        logging.debug(f"Relays - Set {bin(value)}")
        self.shifter.Set_value_8_bit_inv(value)

    def Shift(self, value):
        logging.debug(f"Relays - Shift {bin(value)}")
        self.shifter.Set_value_1_bit(value ^ 1)

    def Stop(self):
        logging.debug("Relays - Stop")
        self.shifter.Set_value_8_bit_inv(0x00)

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
        logging.debug(rgb)
        
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
            logging.debug(rgb)
            self.Update_1_led_strip(rgb)
        self.Send_32_zero()

    def Setup_board(self):
        logging.debug("Led_shifter - Setup_board")
        gpio.setmode(gpio.BOARD)
        gpio.setup(self.data_pin,    OUT)
        gpio.output(self.data_pin,   LOW)
        gpio.setup(self.clock_pin,   OUT)
        gpio.output(self.clock_pin,  LOW)
