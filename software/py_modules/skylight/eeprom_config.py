
import struct

class cfgObject:
    """
    Base class for any object in the configuration EEPROM
    that is referenced indirectly via pointer.
    """
    def __init__(self):
        
        """
        Byte address within EEPROM that this object is located
        """
        self.ee_address = None
    
    #-----------------------------------------------
    def get_all_objects(self):
        """
        Recursively get handles to all cfgObject instances referenced
        Include self.
        If a subclass can reference a child object, it must extend this method.
        """
        obj = [self]
        return(obj)
    
    #-----------------------------------------------
    def is_compilable(self):
        """
        To compile an object, the addresses of any of its children must be known
        Check children (if any)
        If a subclass can reference a child object, it must extend this method.
        """
        return(True)
    
    #-----------------------------------------------
    def to_binary(self):
        """
        Compile object into its binary representation
        """
        raise Exception("Must override this method!")
        
    #-----------------------------------------------
    # Utility Methods
    #-----------------------------------------------
    def __eq__(self, other):
        """ Equal until proven not equal """
        if(type(other) != type(self)):
            return(False)
        return(True)
        
#===================================================================================================
# Lighting Transitions
#===================================================================================================

class Transition(cfgObject):
    """
    Lighting transition base class
    """
    ID = None
    
    def __init__(self):
        cfgObject.__init__(self)
        
        """ Number of ticks of delay before transition starts """
        self.delay = 0
    
    #-----------------------------------------------
    def to_binary(self):
        # uint8_t ID
        # [pad byte]
        # uint16_t delay
        b = struct.pack("<BxH", self.ID, self.delay)
        return(b)
        
    #-----------------------------------------------
    # Utility Methods
    #-----------------------------------------------
    def __eq__(self, other):
        if(not cfgObject.__eq__(self, other)):
            return(False)
        
        if(self.delay != other.delay):
            return(False)
            
        return(True)
    
#---------------------------------------------------------------------------------------------------
class trans_Immediate(Transition):
    ID = 0
    
    def __init__(self, color = (0,0,0,0)):
        Transition.__init__(self)
        
        """ Color setting after transition completes """
        self.color = color
        
    #-----------------------------------------------
    def to_binary(self):
        b = Transition.to_binary(self)
        
        # rgbw_t color:
        #   uint16_t r
        #   uint16_t g
        #   uint16_t b
        #   uint16_t w
        
        b += struct.pack("<HHHH", *self.color)
        return(b)
        
    #-----------------------------------------------
    # Utility Methods
    #-----------------------------------------------
    def __eq__(self, other):
        if(not Transition.__eq__(self, other)):
            return(False)
        
        if(self.color != other.color):
            return(False)
            
        return(True)
    
#---------------------------------------------------------------------------------------------------
class trans_Fade(Transition):
    ID = 1
    
    def __init__(self):
        Transition.__init__(self)
        
        """ Color setting after transition completes """
        self.color = (0,0,0,0)
        
        """ Number of ticks the transition takes """
        self.duration = 0
        
    #-----------------------------------------------
    def to_binary(self):
        b = Transition.to_binary(self)
        
        # rgbw_t color:
        #   uint16_t r
        #   uint16_t g
        #   uint16_t b
        #   uint16_t w
        # uint16_t duration
        
        b += struct.pack("<HHHH", *self.color)
        b += struct.pack("<HHHHH", self.duration)
        return(b)
    #-----------------------------------------------
    # Utility Methods
    #-----------------------------------------------
    def __eq__(self, other):
        if(not Transition.__eq__(self, other)):
            return(False)
        
        if(self.duration != other.duration):
            return(False)
            
        if(self.color != other.color):
            return(False)
            
        return(True)
    
#---------------------------------------------------------------------------------------------------
class trans_Waveform(Transition):
    ID = 2
    
    def __init__(self):
        Transition.__init__(self)
        
        """ Handle to ColorList object """
        self.waveform = ColorList()
        
        """ Number of ticks the transition takes """
        self.duration = 0
        
    #-----------------------------------------------
    def get_all_objects(self):
        obj = Transition.get_all_objects(self)
        
        obj += self.waveform.get_all_objects()
            
        return(obj)
    
    #-----------------------------------------------
    def is_compilable(self):
        
        if(self.waveform.ee_address == None):
            return(False)
        
        return(True)
    
    #-----------------------------------------------
    def to_binary(self):
        b = Transition.to_binary(self)
        
        # eeptr_t waveform
        # uint16_t duration
        
        b += struct.pack("<HH", self.waveform.ee_address, self.duration)
        return(b)
        
    #-----------------------------------------------
    # Utility Methods
    #-----------------------------------------------
    def __eq__(self, other):
        if(not Transition.__eq__(self, other)):
            return(False)
        
        if(self.duration != other.duration):
            return(False)
            
        if(self.waveform != other.waveform):
            return(False)
        
        return(True)

#---------------------------------------------------------------------------------------------------
class ColorList(cfgObject):
    def __init__(self):
        cfgObject.__init__(self)
        
        """
        list of 4-tuples of raw rgbw values
        (r,g,b,w)
        """
        self.colors = [(0,0,0,0)]
        
    #-----------------------------------------------
    def to_binary(self):
        
        # uint8_t n_colors
        # [pack byte]
        b = struct.pack("<Bx", len(self.colors))
        for color in self.colors:
            # rgbw_t color:
            #   uint16_t r
            #   uint16_t g
            #   uint16_t b
            #   uint16_t w
            b += struct.pack("<HHHH", *self.colors)
            
        return(b)
        
    #-----------------------------------------------
    # Utility Methods
    #-----------------------------------------------
    def __eq__(self, other):
        if(not cfgObject.__eq__(self, other)):
            return(False)
        
        if(self.colors != other.colors):
            return(False)
        
        return(True)
    
#===================================================================================================
# ModeSets
#===================================================================================================
class ModeSet(cfgObject):
    def __init__(self):
        cfgObject.__init__(self)
        
        """
        List of 2-tuples of handles to on/off transition objects
        (on_transition, off_transition)
        """
        self.modes = [
            (
                trans_Immediate((0,0,0,0xFFFF)),
                trans_Immediate((0,0,0,0))
            )
        ]
        
    #-----------------------------------------------
    def get_all_objects(self):
        obj = cfgObject.get_all_objects(self)
        
        for mode in self.modes:
            obj += mode[0].get_all_objects()
            obj += mode[1].get_all_objects()
        
        return(obj)
    
    #-----------------------------------------------
    def is_compilable(self):
        
        for mode in self.modes:
            if((mode[0].ee_address == None) or (mode[1].ee_address == None)):
                return(False)
        
        return(True)
        
    #-----------------------------------------------
    def to_binary(self):
        
        # uint8_t n_modes
        # [pack byte]
        b = struct.pack("<Bx", len(self.modes))
        for mode in self.modes:
            # mode_entry_t
            #   eeptr_t on_transition
            #   eeptr_t off_transition
            b += struct.pack("<HH", mode[0].ee_address, mode[1].ee_address)
            
        return(b)
        
    #-----------------------------------------------
    # Utility Methods
    #-----------------------------------------------
    def __eq__(self, other):
        if(not cfgObject.__eq__(self, other)):
            return(False)
        
        if(self.modes != other.modes):
            return(False)
        
        return(True)
        
#===================================================================================================
# Alarm Tables
#===================================================================================================

class AlarmEntry:
    def __init__(self):
        
        """
        List of days of the week that the alarm fires.
        Each DOW in list is a number 0-6
        0=Sunday
        """
        self.dow_list = []
        
        """
        Hour that the alarm should fire (0-23)
        """
        self.hour = 0
        
        """
        Minute that the alarm should fire (0-59)
        """
        self.minute = 0
        
        """
        Handle to object related to this alarm
        """
        self.data = None
    
    #-----------------------------------------------
    def to_binary(self):
        
        # Collapse dow_list into bit mask
        dow_mask = 0
        for dow in self.dow_list:
            dow_mask |= 2**dow
        
        # uint8_t dayofweek_mask
        # uint8_t hour
        # uint8_t minute
        # [pack byte]
        # eeptr_t data
        b = struct.pack("<BBBxH", dow_mask, self.hour, self.minute, self.data.ee_address)
        return(b)
        
    #-----------------------------------------------
    # Utility Methods
    #-----------------------------------------------
    def __eq__(self, other):
        """ Equal until proven not equal """
        if(type(other) != type(self)):
            return(False)
            
        if(set(self.dow_list) != set(other.dow_list)):
            return(False)
        
        if(self.hour != other.hour):
            return(False)
            
        if(self.minute != other.minute):
            return(False)
            
        if(self.data != other.data):
            return(False)
            
        return(True)
        
#---------------------------------------------------------------------------------------------------
class AlarmTable(cfgObject):
    def __init__(self):
        cfgObject.__init__(self)
        
        """
        List of AlarmEntry items
        """
        self.alarms = []
        
    #-----------------------------------------------
    def get_all_objects(self):
        obj = cfgObject.get_all_objects(self)
        
        for alarm in self.alarms:
            if(alarm.data):
                obj += alarm.data.get_all_objects()
        
        return(obj)
    
    #-----------------------------------------------
    def is_compilable(self):
        
        for alarm in self.alarms:
            if(alarm.data == None):
                return(False)
            elif(alarm.data.ee_address == None):
                return(False)
        
        return(True)
        
    #-----------------------------------------------
    def to_binary(self):
        
        # uint8_t n_items
        # [pack byte]
        b = struct.pack("<Bx", len(self.alarms))
        for alarm in self.alarms:
            b += alarm.to_binary()
            
        return(b)
    #-----------------------------------------------
    # Utility Methods
    #-----------------------------------------------
    def __eq__(self, other):
        if(not cfgObject.__eq__(self, other)):
            return(False)
        
        if(self.alarms != other.alarms):
            return(False)
        
        return(True)
        
#===================================================================================================
class eeConfig:
    def __init__(self):
        
        """
        Handle to default ModeSet
        """
        self.default_modeset = ModeSet()
        
        """
        Handle to Lighting Alarm Table
        """
        self.lighting_alarm_table = AlarmTable()
        
        """
        Handle to Lighting Alarm Table
        """
        self.modeset_change_table = AlarmTable()
        
    #-----------------------------------------------
    def to_binary(self, dummy = False):
        
        # uint32_t timestamp
        # eeptr_t default_modeset
        # eeptr_t lighting_alarm_table
        # eeptr_t modeset_change_table
        # [pack byte 2x]
        if(dummy):
            b = struct.pack("<IHHHxx", 0, 0, 0, 0)
        else:
            b = struct.pack("<IHHHxx", 0,
                                self.default_modeset.ee_address,
                                self.lighting_alarm_table.ee_address,
                                self.modeset_change_table.ee_address,
                            )
        
        return(b)
        
    #-----------------------------------------------
    def get_all_objects(self):
        obj = self.default_modeset.get_all_objects()
        obj += self.lighting_alarm_table.get_all_objects()
        obj += self.modeset_change_table.get_all_objects()
        
        return(obj)


#===================================================================================================
def compile(cfg):
    """
    Compile the configuration into an EEPROM image
    """
    if(type(cfg) != eeConfig):
        raise TypeError("cfg must be an instance of eeConfig")
    
    # Create dummy header for now
    image = cfg.to_binary(dummy=True)
    ee_address = len(image)
    
    # Collect a list of all cfgObject instances in the entire configuration
    uncompiled = cfg.get_all_objects()
    
    # Reset each object's compile state (Make sure their ee_address are all None)
    for o in uncompiled:
        o.ee_address = None
    
    # Loop until all objects have been compiled
    compiled = []
    while(len(uncompiled) != 0):
        still_uncompiled = []
        for o in uncompiled:
            if(o.is_compilable()):
                # Compile the object
                
                # First, check if an equivalent copy of the object already exists
                for co in compiled:
                    if(o == co):
                        # An equivalent object has already been compiled.
                        # Reuse that object by sharing the reference to it
                        o.ee_address = co.ee_address
                        break
                else:
                    # An equivalent does not exist.
                    # Compile it.
                    
                    # Append to EEPROM image and assign the resulting ee_address
                    b = o.to_binary()
                    o.ee_address = ee_address
                    ee_address += len(b)
                    image += b
                    
                    # Save to compiled list for potential reuse
                    compiled.append(o)
                
            else:
                # Not compilable yet. Set aside
                still_uncompiled.append(o)
        
        # Finished loop through uncompiled list
        if(not len(still_uncompiled) < len(uncompiled)):
            # This pass did not accomplish anything!
            raise Exception("Compile is stuck! Pass did not make any progress")
        
        uncompiled = still_uncompiled
    
    # Finished compiling objects.
    # Replace header with actual header
    hdr = cfg.to_binary()
    image = hdr + image[len(hdr):]
    
    return(image)
