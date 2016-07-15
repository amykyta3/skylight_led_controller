
import json

from ..python_modules import encodable_class as ec
from . import eeprom_config as eecfg

#---------------------------------------------------------------------------------------------------
class Skylight_Settings(ec.EncodableClass):
    encode_schema = {
        "cfg": eecfg.eeConfig,
        "t_list": [eecfg.Transition],
        "bt_addr": str
    }
    
    def __init__(self):
        
        # Skylight configuration object
        self.cfg = eecfg.eeConfig()
        
        # Pool of available transitions
        self.t_list = []
        
        # Bluetooth device address
        self.bt_addr = None
        
    @classmethod
    def from_json(cls, filename):
        with open(filename, 'r') as f:
            D = json.load(f)
        
        return(cls.from_dict(D))
        
    def save_json(self, filename):
        D = self.to_dict()
        with open(filename, 'w') as f:
            json.dump(D, f, indent=2, sort_keys = True)

#--------------------------------------------------------------------------------------------------s

# Handle to Skylight_Settings data object
S_DATA = None

BT_LINK = None