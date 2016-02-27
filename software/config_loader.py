#!/usr/bin/env python3

import sys
import argparse
import logging
import json
import py_modules.skylight as skylight
from py_modules.python_modules.app import App

class ConfigLoader(App):
  def set_cmdline_args(self, parser):
    App.set_cmdline_args(self, parser)
    
    parser.description = "Skylight LED Firmware Loader"
    parser.add_argument("-p --port", dest="port", default="/dev/rfcomm0",
                        help="Serial Port Device")
    parser.add_argument("filename",
                        help="Configuration file")
  
  def main(self):
    App.main(self)
    
    # Load and compile config image
    with open(self.options.filename, 'r') as f:
        D = json.load(f)
    
    Cfg = skylight.eeConfig.from_dict(D)
    image = skylight.eeprom_config.compile(Cfg)
    
    with skylight.btLink(self.options.port) as S:
      S.send_config(image)

####################################################################################################
if __name__ == '__main__':
  A = ConfigLoader()
  A.main()
