#!/usr/bin/env python3

import sys
import argparse
import logging
import py_modules.skylight.btLink as btLink
from py_modules.python_modules.app import App

class FirmwareLoader(App):
    def set_cmdline_args(self, parser):
        App.set_cmdline_args(self, parser)
        
        parser.description = "Skylight LED Firmware Loader"
        parser.add_argument("-a --addr", dest="addr", default=None,
                            help="Bluetooth Hardware Address")
        parser.add_argument("filename",
                            help="Source Intel-Hex file")
  
    def main(self):
        App.main(self)
        
        # Autodiscover device if necessary
        if(self.options.addr == None):
            self.log.info("Bluetooth address not specified. Searching for matching device...")
            devs = btLink.discover()
            if(len(devs) == 0):
                self.log.error("No devices found")
                sys.exit(1)
            else:
                self.log.info("Using device: %s - %s" % (devs[0][0], devs[0][1]))
                self.options.addr = devs[0][0]
        
        with btLink.btLink(self.options.addr) as S:
            S.enter_bootloader()
            S.send_ihex(self.options.filename)
            S.exit_bootloader()
            S.set_time()

####################################################################################################
if __name__ == '__main__':
    A = FirmwareLoader()
    A.main()
