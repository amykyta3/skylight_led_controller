
import serial
import logging
import time
import binascii

class CMDError(Exception):
    pass

class btLink:
    def __init__(self, port, timeout = 10):
        self.S = serial.Serial()
        self.S.port = port
        self.S.timeout = timeout
        self.S.baudrate = 115200
        self.log = logging.getLogger("skylight")
        
    #-----------------------------------------------------------------------------------------------
    def __enter__(self):
        self.open()
        return(self)
    
    #-----------------------------------------------------------------------------------------------
    def __exit__(self, type, value, traceback):
        self.close()
    
    #-----------------------------------------------------------------------------------------------
    def open(self):
        self.S.open()
        
        # flush out any partial commands
        try:
            self.cmd("\r\n")
        except CMDError:
            # ignore.
            pass
        
        try:
            self.cmd("echo 0\r\n")
        except CMDError:
            # ignore.
            pass
    
    #-----------------------------------------------------------------------------------------------
    def close(self):
        self.S.close()
    
    #-----------------------------------------------------------------------------------------------
    def cmd(self, cmd_string):
        """
        Sends command string and waits for response
        Response ends once '>' is received
        If response spans multiple lines, splits into a list
        If no response, returns ""
        If timeout, raises TimeoutError
        If last line of response is "ERR", raises IOError 
        """
        self.log.debug("cmd: %s" % cmd_string.strip())
        cmd_string = cmd_string.encode("ascii")
        self.S.reset_input_buffer()
        self.S.write(cmd_string)
        
        # Collect response
        resp = []
        resp_line = ""
        
        c = self.S.read(1).decode("ascii")
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
                    self.log.debug("resp_line: %s" % resp_line)
                    resp.append(resp_line)
                    resp_line = ""
            else:
                resp_line += c
            
            c = self.S.read(1).decode("ascii")
        
        if(len(resp_line) != 0):
            self.log.debug("resp_line: %s" % resp_line)
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
    
    #-----------------------------------------------------------------------------------------------
    def enter_bootloader(self):
        """
        Check if in bootloader. If not, enter it
        """
        
        if(self.cmd("id\r\n") == "BL"):
            return
        
        self.cmd("reset\r\n")
            
        if(self.cmd("id\r\n") != "BL"):
            raise CMDError("Failed to enter bootloader")

    #-----------------------------------------------------------------------------------------------
    def exit_bootloader(self):
        """
        Check if in bootloader. If so, exit it
        """
        
        if(self.cmd("id\r\n") != "BL"):
            return
        
        self.cmd("boot\r\n")
            
        if(self.cmd("id\r\n") == "BL"):
            raise CMDError("Failed to exit bootloader")
    
    #-----------------------------------------------------------------------------------------------
    def send_ihex(self, filename):
        self.log.info("Sending file: %s" % filename)
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                self.cmd("ihex %s\r\n" % line)
        
    #-----------------------------------------------------------------------------------------------
    def set_time(self):
        now = time.localtime()
        self.cmd("set_time %x %x %x %x %x %x\r\n" % (
            now.tm_year,
            now.tm_mon,
            now.tm_mday,
            now.tm_hour,
            now.tm_min,
            now.tm_sec
        ))
        
        self.cmd("set_dst %d %d\r\n" % (time.daylight, now.tm_isdst))
    
    #-----------------------------------------------------------------------------------------------
    def set_rgbw(self, color):
        rgbw = color.get_rgbw()
        self.cmd("rgbw %x %x %x %x\r\n" % rgbw)
        
    #-----------------------------------------------------------------------------------------------
    def send_config(self, image):
        
        # Pad image to be a multiple of the page size (32-bytes)
        if((len(image)%32) != 0):
            image += b"\xFF" * (32 - len(image)%32)
        
        self.cmd("cfg_erase\r\n")
        
        for addr in range(0, len(image), 32):
            page = addr/32
            hex_str = binascii.hexlify(image[addr:addr+32]).decode('ascii')
            self.cmd("cfg_write %X %s\r\n" % (page, hex_str))
        
        self.cmd("cfg_reload\r\n")
    
    #-----------------------------------------------------------------------------------------------
    def sample_chroma(self, T_i):
        """
        Takes a single color sample from the VEML6040 sensor.
        """
        resp = self.cmd("chroma %X\r\n" % T_i)
        resp = resp.split()
        for i,v in enumerate(resp):
            resp[i] = int(v,16)
        return(resp)
        
    def measure_chroma(self, n_average = 1):
        """
        Takes a color measurement from the VEML6040 sensor using the best possible integration time
         1. Takes several samples to determine ideal integration time for maximum resolution
         2. Takes additional samples as necessary to get an average
        """
        
        # Determine best T_i
        T_i = 3
        retry_count = 3
        while(retry_count > 0):
            sample = self.sample_chroma(T_i)
            print(sample)
            print("Sampled at T_i=%d, Max=0x%04X" % (T_i, max(sample)))
            
            T_i_prev = T_i
            
            if(max(sample) > (0x10000*0.90)):
                # T_i is too long for the brightness
                if(T_i == 0):
                    # T_i is already at the lowest setting.
                    break
                
                T_i -= 1
            elif(max(sample) < (0x8000*0.90)):
                # Could use a longer T_i
                if(T_i == 5):
                    # T_i is already at the highest setting.
                    break
                
                T_i += 1
            else:
                # Sample is within decent range
                break
                
            retry_count -= 1
            
            # VEML6040 seems to need some time between switching integration times
            time.sleep(0.040 * (2**T_i_prev))
        
        # Do additional samples to average
        extra_samples = n_average-1
        sample_list = [sample]
        while(extra_samples > 0):
            sample_list.append(self.sample_chroma(T_i))
            extra_samples -= 1
        
        # Post process samples
        # - Take average
        # - Normalize scale based on T_i used
        result = [0,0,0,0]
        for s in sample_list:
            for i,c in enumerate(s):
                result[i] += c
        for i,c in enumerate(result):
            c *= 2**(5-T_i)
            result[i] = c/n_average
            
        return(result)
        