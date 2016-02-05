#!/usr/bin/env python3

import sys
import argparse
import logging
import py_modules.skylight as skylight

logging.basicConfig(
    format="%(levelname)s:%(name)s - %(message)s",
    level=logging.INFO
)
log = logging.getLogger()

class App:
    
    def __init__(self):
        self.options = None
    
    def main(self):
        self.get_args()
        
        with skylight.Skylight(self.options.port) as S:
            S.enter_bootloader()
            S.send_ihex(self.options.filename)
            S.exit_bootloader()
            S.set_time()
        
    def get_args(self):
        p = argparse.ArgumentParser(description="Skylight LED Firmware Loader")
        p.add_argument("-p --port", dest="port", default="/dev/rfcomm0",
                        help="Serial Port Device")
        p.add_argument("-q --quiet", dest="quiet", action="store_true", default=False,
                        help="Disable info messages")
        p.add_argument("--verbose", dest="verbose", action="store_true", default=False,
                        help="Enable debug messages")
        p.add_argument("filename",
                        help="Source Intel-Hex file")
        self.options = p.parse_args()
        
        if(self.options.quiet):
            log.setLevel(logging.WARNING)
        elif(self.options.verbose):
            log.setLevel(logging.DEBUG)

####################################################################################################
if __name__ == '__main__':
    A = App()
    A.main()
