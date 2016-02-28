#!/usr/bin/env python3

import sys
import argparse
import logging
import py_modules.skylight as skylight
from py_modules.python_modules.app import App

class FirmwareLoader(App):
    def set_cmdline_args(self, parser):
        App.set_cmdline_args(self, parser)
        
        parser.description = "Skylight LED Firmware Loader"
        parser.add_argument("-p --port", dest="port", default="/dev/rfcomm0",
                            help="Serial Port Device")
        parser.add_argument("filename",
                            help="Source Intel-Hex file")
  
    def main(self):
        App.main(self)
    
        with skylight.btLink(self.options.port) as S:
            S.enter_bootloader()
            S.send_ihex(self.options.filename)
            S.exit_bootloader()
            S.set_time()

####################################################################################################
if __name__ == '__main__':
    A = FirmwareLoader()
    A.main()
