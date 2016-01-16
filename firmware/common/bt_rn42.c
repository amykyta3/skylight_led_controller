

#include <stdint.h>
#include <string.h>

#define F_CPU 32000000UL
#include <util/delay.h>

#include <uart_io.h>
#include "bt_rn42.h"

#define TIMEOUT_MS 500

//--------------------------------------------------------------------------------------------------
/**
 * \brief Send a raw command to RN42. Waits until response arrives
 * 
 * All RN42 responses are terminated with \\r\\n. Response
 * is all text before this.
 * 
 * \param cmd       Command string
 * \param resp      Response buffer
 * \param resp_size Maximum response size
 * \retval 0 OK!
 * \retval 1 Timed out
 **/
static uint8_t raw_cmd(const char *cmd, char *resp, uint8_t resp_size){
    
    uart_rdflush();
    uart_puts(cmd);
    
    while(1){
        uint16_t timeout;
        char c;
        
        // Get next char
        timeout = TIMEOUT_MS;
        while(uart_rdcount() == 0){
            _delay_ms(1);
            timeout--;
            if(timeout == 0){
                return(1);
            }
        }
        c = uart_getc();
        
        if(c == '\r'){
            // discard
        }else if(c == '\n'){
            // End of response. Terminate
            *resp = 0;
            return(0);
        }else{
            resp_size--;
            if(resp_size == 0){
                *resp = 0;
                return(0);
            }else{
                *resp = c;
                resp++;
            }
        }
    }
}

//--------------------------------------------------------------------------------------------------
uint8_t bt_enter_cmd_mode(void){
    char resp[4];
    uint8_t ret;
    
    ret = raw_cmd("$$$", resp, sizeof(resp));
    if(ret == 0){
        // Got response. Verify
        if(strcmp(resp, "CMD")) return(1);
    }else{
        // No response... might already be in command mode
        // try sending additional \r to try to flush it out
        // This definitely shouldnt time out
        if(raw_cmd("\r", resp, sizeof(resp))) return(1);
        if(strcmp(resp, "?")) return(1);
    }
    
    return(0);
}

//--------------------------------------------------------------------------------------------------
void bt_exit_cmd_mode(void){
    char resp[4];
    raw_cmd("---\r", resp, sizeof(resp));
}

//--------------------------------------------------------------------------------------------------
uint8_t bt_reboot(void){
    char resp[8];
    if(raw_cmd("R,1\r", resp, sizeof(resp))) return(1);
    if(strcmp(resp, "Reboot!")) return(1);
    return(0);
}

//--------------------------------------------------------------------------------------------------
uint8_t bt_S_cmd(const char *cmd){
    char resp[4];
    if(raw_cmd(cmd, resp, sizeof(resp))) return(1);
    if(strcmp(resp, "AOK")) return(1);
    return(0);
}
