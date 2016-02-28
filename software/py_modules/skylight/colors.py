
from ..python_modules import class_codec

class Color(class_codec.encodable_class):
    
    _encode_schema = {}
    
    def get_rgbw(self):
        """
        Returns a 4-tuple containing the raw integer RGBW LED values
        """
        # Override this
        return((0,0,0,0))
        
    #-----------------------------------------------
    # Utility Methods
    #-----------------------------------------------
    def __eq__(self, other):
        raise Exception("TODO")
        if(not Transition.__eq__(self, other)):
            return(False)
        
        if(self.color != other.color):
            return(False)
            
        return(True)
        
class Color_raw(Color):
    _encode_schema = {
        "r":int,
        "g":int,
        "b":int,
        "w":int
    }
    
    def __init__(self, r, g, b, w):
        
        if(not (type(r) == type(g) == type(b) == type(w) == int)):
            raise TypeError("rgbw values must be of type int")
            
        if(not ((min(r,g,b,w) >= 0) and (max(r,g,b,w) <= 0xFFFF))):
            raise ValueError("rgbw values must be between 0x0000 and 0xFFFF")
        
        self.r = r
        self.g = g
        self.b = b
        self.w = w
        
    def get_rgbw(self):
        return((self.r, self.g, self.b, self.w))
        
class Color_rgb(Color):
    _encode_schema = {
        "r":float,
        "g":float,
        "b":float
    }
    
    def __init__(self, r, g, b):
        if(type(r) == type(g) == type(b) == int):
            # Assume 0-255. Convert to float
            if(not ((min(r,g,b) >= 0) and (max(r,g,b) <= 255))):
                raise ValueError("Integer rgb values must be between 0 and 255")
            
            r = float(r)/255.0
            g = float(g)/255.0
            b = float(b)/255.0
            
        elif(type(r) == type(g) == type(b) == float):
            if(not ((min(r,g,b) >= 0.0) and (max(r,g,b) <= 1.0))):
                raise ValueError("Float rgb values must be between 0.0 and 1.0")
        else:
            raise TypeError("rgbw values must all be of type int or float")
        
        self.r = r
        self.g = g
        self.b = b
        
    def get_rgbw(self):
        # Map RGB to LED RGBW
        # Do a dumb conversion for now.
        
        whiteness = min(self.r, self.g, self.b)
        r_offset = self.r - whiteness
        g_offset = self.g - whiteness
        b_offset = self.b - whiteness
        
        raw_r = int(r_offset * 0xFFFF)
        raw_g = int(g_offset * 0xFFFF)
        raw_b = int(b_offset * 0xFFFF)
        raw_w = int(whiteness * 0xFFFF)
        
        return((raw_r, raw_g, raw_b, raw_w))
        