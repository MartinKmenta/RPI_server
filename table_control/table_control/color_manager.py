import random
import logging


COLORS = {
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


class Rgb():
    """
    Class for managing colors
    """
    
    def __init__(self, r = 0, g = 0, b = 0):
        """
        initializes Rgb class with setter
        """
        
        self.r = self.Set(r)
        self.g = self.Set(g)
        self.b = self.Set(b)
    
    def __str__(self):
        return str(self.to_dict())
    
    def __repr__(self):
        return repr(self.to_dict())
        
    @staticmethod
    def from_list(rgb_list: list = list()):
        """
        sets rgb class parameters from list
        bounds checked with setter
        """
        return Rgb(*rgb_list)
    
    def to_list(self):
        """
        returns list of class parameters
        added for consistency reasons
        """
        
        return [self.r,self.g,self.b]
    
    @staticmethod
    def from_dict(rgb_dict: dict = {"r" : 0, "g" : 0, "b" : 0}):
        """
        sets rgb class parameters from dict
        bounds checked with setter
        """
        return Rgb(**rgb_dict)

    def to_dict(self):
        """
        returns dict of class parameters
        added for consistency reasons
        """
        
        return {"r" : self.r, "g" : self.g, "b" : self.b}
    
    @staticmethod
    def FromColor(color: str = "default"):
        """
        input: name of color
        output: corresponding color
        """
        
        color = color.lower()
        
        if(color in COLORS):
            rgb_dict = COLORS[color]
        else:
            logging.error(f"Rgb ERROR - unknown color: {color}")
            rgb_dict = COLORS["default"]

        return Rgb.from_dict(rgb_dict) 
    
    @staticmethod
    def FromHex(color: str = "#000000"):
        """
        accepts string in formats: #000000, 0x000000
        returns Rgb object
        """
        
        color = color.lower()
        
        logging.debug(f'Rgb - FromHex: {color}')
        try:
            if color.startswith("#"):
                color = color.replace("#", "0x")
                
            hex_color = int(color, base=16)
            
            r = int((hex_color & 0xff0000) >> 16)
            g = int((hex_color & 0xff00) >> 8)
            b = int(hex_color & 0xff)
            
            return Rgb.from_list([r,g,b]) 
        
        except:
            logging.error(f'Rgb - FromHex - unable to decode color: {color}')
            return Rgb() # returns Rgb(0,0,0) doesn't raise error
        
    def Set(self, val: int = 0):
        """Checks if 0 <= val < 256""" 
        return 255 if (val > 255) else (0 if (val < 0) else int(val))

    @staticmethod
    def FromRandom(seed = None):
        random.seed(seed)
        """generates random color"""
        return Rgb.from_list([random.randint(0, 256) for x in range(3)])
    
    # def Random(self):   return Rgb(random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))
    # def White(self):    return Rgb(255, 255, 255)
    # def Red(self):      return Rgb(255,   0,   0)
    # def Green(self):    return Rgb(  0, 255,   0)
    # def Blue(self):     return Rgb(  0,   0, 255)
    # def Cyan(self):     return Rgb(  0, 255, 255)
    # def Magenta(self):  return Rgb(255,   0, 255)
    # def Yellow(self):   return Rgb(255, 255,   0)
    # def Black(self):    return Rgb(  0,   0,   0)

def _test():
    Rgb()
    Rgb(255,255,255)
    
    x = [255,255,255]
    x_rgb = Rgb.from_list(x)
    assert x == x_rgb.to_list()
    
    y = {"r" : 255, "g" : 255, "b" : 255}
    y_rgb = Rgb.from_dict(y)
    assert y == y_rgb.to_dict()

    assert Rgb.FromColor().to_dict() == COLORS["default"]
    
    Rgb.FromColor("not_existing_color")
    
    Rgb.FromHex("#FFFFFF")
    
    print("Random color\t", Rgb.FromRandom(42))
        
if __name__ == "__main__":
    _test()
