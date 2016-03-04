
import struct
from ..python_modules import class_codec
from . import colors

#===================================================================================================
# Microcontroller Constants
#===================================================================================================

MAPPED_EEPROM_START = 0x1000
TICKS_PER_SECOND = 64

#===================================================================================================
class cfgObject(class_codec.encodable_class):
    """
    Base class for any object in the configuration EEPROM
    that is referenced indirectly via pointer.
    """
    
    _encode_schema = {
        "name": str
    }
    
    def __init__(self):
        
        self.name = ""
        
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
    
    _encode_schema = {
        "delay":float
    }
    
    def __init__(self):
        cfgObject.__init__(self)
        
        """ Number of seconds of delay before transition starts """
        self.delay = 0.0
    
    #-----------------------------------------------
    def to_binary(self):
        
        # Convert delay seconds into ticks
        delay_ticks = int(self.delay * TICKS_PER_SECOND)
        
        # uint8_t ID
        # uint16_t delay
        b = struct.pack("<BH", self.ID, delay_ticks)
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
    
    _encode_schema = {
        "color": colors.Color
    }
    
    def __init__(self):
        Transition.__init__(self)
        
        """ Color setting after transition completes """
        self.color = colors.Color_rgb(0,0,0)
        
    #-----------------------------------------------
    def to_binary(self):
        rgbw_tuple = self.color.get_rgbw()
        
        b = Transition.to_binary(self)
        
        # rgbw_t color:
        #   uint16_t r
        #   uint16_t g
        #   uint16_t b
        #   uint16_t w
        b += struct.pack("<HHHH", *rgbw_tuple)
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
    
    _encode_schema = {
        "color": colors.Color,
        "duration":float
    }
    
    def __init__(self):
        Transition.__init__(self)
        
        """ Color setting after transition completes """
        self.color = colors.Color_rgb(0,0,0)
        
        """ Number of seconds the transition takes """
        self.duration = 1.0
        
    #-----------------------------------------------
    def to_binary(self):
        
        # Convert duration seconds into ticks
        duration_ticks = int(self.duration * TICKS_PER_SECOND)
        
        rgbw_tuple = self.color.get_rgbw()
        
        b = Transition.to_binary(self)
        
        # rgbw_t color:
        #   uint16_t r
        #   uint16_t g
        #   uint16_t b
        #   uint16_t w
        # uint16_t duration
        b += struct.pack("<HHHH", *rgbw_tuple)
        b += struct.pack("<H", duration_ticks)
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
class ColorList(cfgObject):
    
    _encode_schema = {
        "colors":[colors.Color]
    }
    
    def __init__(self):
        cfgObject.__init__(self)
        
        """
        list of colors
        """
        self.colors = [colors.Color_rgb(0,0,0)]
        
    #-----------------------------------------------
    def to_binary(self):
        
        # uint8_t n_colors
        b = struct.pack("<B", len(self.colors))
        for color in self.colors:
            rgbw_tuple = color.get_rgbw()
            
            # rgbw_t color:
            #   uint16_t r
            #   uint16_t g
            #   uint16_t b
            #   uint16_t w
            b += struct.pack("<HHHH", *rgbw_tuple)
            
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

#---------------------------------------------------------------------------------------------------
class trans_Waveform(Transition):
    ID = 2
    
    _encode_schema = {
        "waveform":ColorList,
        "duration":float
    }
    
    def __init__(self):
        Transition.__init__(self)
        
        """ Handle to ColorList object """
        self.waveform = ColorList()
        
        """ Number of ticks the transition takes """
        self.duration = 0.0
        
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
        
        # Convert duration seconds into ticks
        duration_ticks = int(self.duration * TICKS_PER_SECOND)
        
        # uintptr_t waveform
        # uint16_t duration_ticks
        b += struct.pack("<HH", self.waveform.ee_address, duration_ticks)
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
    
#===================================================================================================
# ModeSets
#===================================================================================================
class ModeSet(cfgObject):
    
    _encode_schema = {
        "modes":[(Transition,Transition)]
    }
    
    def __init__(self):
        cfgObject.__init__(self)
        
        """
        List of 2-tuples of handles to on/off transition objects
        (on_transition, off_transition)
        """
        self.modes = []
        
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
        b = struct.pack("<B", len(self.modes))
        for mode in self.modes:
            # mode_entry_t
            #   uintptr_t on_transition
            #   uintptr_t off_transition
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

class AlarmEntry(class_codec.encodable_class):
    
    _encode_schema = {
        "name":str,
        "dow_list":[int],
        "hour":int,
        "minute":int,
        "data":cfgObject
    }
    
    def __init__(self):
        
        self.name = ""
        
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
        # uintptr_t data
        b = struct.pack("<BBBH", dow_mask, self.hour, self.minute, self.data.ee_address)
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
    
    _encode_schema = {
        "alarms":[AlarmEntry]
    }
    
    def __init__(self):
        cfgObject.__init__(self, "N/A")
        
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
        b = struct.pack("<B", len(self.alarms))
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
class eeConfig(class_codec.encodable_class):
    
    _encode_schema = {
        "default_modeset":ModeSet,
        "lighting_alarm_table":AlarmTable,
        "modeset_change_table":AlarmTable
    }
    
    def __init__(self):
        
        """
        Handle to default ModeSet
        """
        self.default_modeset = ModeSet("default")
        
        """
        Handle to Lighting Alarm Table
        """
        self.lighting_alarm_table = AlarmTable()
        
        """
        Handle to Lighting Alarm Table
        """
        self.modeset_change_table = AlarmTable()
        
        # Configure default modeset to something sane
        t_on = trans_Immediate()
        t_off = trans_Immediate()
        t_on.color = colors.Color_raw(0x0000,0x0000,0x0000,0xFFFF)
        self.default_modeset.modes = [(t_on, t_off)]
        
    #-----------------------------------------------
    def to_binary(self, dummy = False):
        
        # uint32_t timestamp
        # uintptr_t default_modeset
        # uintptr_t lighting_alarm_table
        # uintptr_t modeset_change_table
        if(dummy):
            b = struct.pack("<IHHH", 0, 0, 0, 0)
        else:
            b = struct.pack("<IHHH", 0,
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

    #-----------------------------------------------
    def compile(self):
        """
        Compile the configuration into an EEPROM image
        """
        
        # Initialize EEPROM address
        ee_address = MAPPED_EEPROM_START
        
        # Create dummy header for now
        image = self.to_binary(dummy=True)
        ee_address += len(image)
        
        # Collect a list of all cfgObject instances in the entire configuration
        uncompiled = self.get_all_objects()
        
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
        hdr = self.to_binary()
        image = hdr + image[len(hdr):]
        
        if(len(image) > 2048):
            raise Exception("Configuration image exceeds 2kB. Will not fit in EEPROM")
        
        return(image)
