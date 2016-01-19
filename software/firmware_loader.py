#!/usr/bin/env python3

import sys
import os
import serial
import argparse
import logging

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
        
        with open(self.options.filename, 'r') as f:
            with serial.Serial() as S:
                log.info("Connecting to device at: %s" % self.options.port)
                S.port = self.options.port
                S.timeout = 10
                S.baudrate = 115200
                try:
                    S.open()
                except serial.serialutil.SerialException:
                    log.critical("Could not open port: %s" % self.options.port)
                    sys.exit(1)
                
                log.info("Entering bootloader")
                # Make sure device is in bootloader
                
                # flush out any partial commands
                try:
                    cmd(S,"\r\n")
                except CMDError:
                    # ignore.
                    pass
                if(cmd(S,"id\r\n") != "BL"):
                    cmd(S, "reset\r\n")
                
                # Send HEX file
                log.info("Sending file: %s" % self.options.filename)
                for line in f:
                    line = line.strip()
                    cmd(S, "ihex %s\r\n" % line)
                    
                # Boot!
                log.info("Starting application")
                cmd(S, "boot\r\n")
        
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

#---------------------------------------------------------------------------------------------------
class CMDError(Exception):
    pass

def cmd(S, cmd_string):
    """
    Sends command string and waits for response
    Response ends once '>' is received
    If response spans multiple lines, splits into a list
    If no response, returns ""
    If timeout, raises TimeoutError
    If last line of response is "ERR", raises IOError 
    """
    log.debug("cmd: %s" % cmd_string.strip())
    cmd_string = cmd_string.encode("ascii")
    S.reset_input_buffer()
    S.write(cmd_string)
    
    # Collect response
    resp = []
    resp_line = ""
    
    c = S.read(1).decode("ascii")
    while(c != '>'):
        if(c == ''):
            # Timed out
            raise TimeoutError("Timed out waiting for a response")
        elif(c == '\r'):
            # discard
            pass
        elif(c == '\n'):
            # Got newline
            if(len(resp_line) != 0):
                log.debug("resp_line: %s" % resp_line)
                resp.append(resp_line)
                resp_line = ""
        else:
            resp_line += c
        
        c = S.read(1).decode("ascii")
    
    if(len(resp_line) != 0):
        log.debug("resp_line: %s" % resp_line)
        resp.append(resp_line)
        resp_line = ""
    
    # if no response, fill with empty
    if(len(resp) == 0):
        resp = [""]
        
    # Check if last line is error response
    if(resp[len(resp)-1] == "ERR"):
        raise CMDError("Command responded with an error")
    
    # If one response line, collapse
    elif(len(resp) == 1):
        resp = resp[0]
    
    return(resp)

####################################################################################################
if __name__ == '__main__':
    A = App()
    A.main()
