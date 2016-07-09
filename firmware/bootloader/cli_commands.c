#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include <avr/io.h>
#include <avr/interrupt.h>

#include <cli_commands.h>
#include <uart_io.h>
#include <self_program.h>
#include <intel_hex.h>
#include <board.h>

//==================================================================================================
// Device-specific output functions
//==================================================================================================

void cli_puts(char *str){
    uart_puts(str);
}

void cli_putc(char chr){
    uart_putc(chr);
}

void cli_print_prompt(void){
    uart_puts("\r\n>");
}

void cli_print_error(int error){
    uart_puts("ERR");
}

void cli_print_notfound(char *strcmd){
    uart_puts("ERR");
}

//==================================================================================================
// Custom Commands
//==================================================================================================
void start_app(void);

int cmd_boot(uint8_t argc, char *argv[]){
    start_app();
    return(1); // if got here, boot failed
}

//--------------------------------------------------------------------------------------------------
int cmd_id(uint8_t argc, char *argv[]){
    cli_puts("BL");
    return(0);
}

//--------------------------------------------------------------------------------------------------
int cmd_led(uint8_t argc, char *argv[]){
    if(argc != 2){
        return(1);
    }
    
    if(argv[1][0] == '1'){
        PORTA.OUTSET = P_LED_bm;
    }else if(argv[1][0] == '0'){
        PORTA.OUTCLR = P_LED_bm;
    }else{
        return(1);
    }
    return(0);
}

//--------------------------------------------------------------------------------------------------
int cmd_reset(uint8_t argc, char *argv[]){
    // Disable Interrupt
    cli();
    
    // Reset
    _PROTECTED_WRITE(RST.CTRL, RST_SWRST_bm);
    return(0);
}

//--------------------------------------------------------------------------------------------------
int cmd_ihex(uint8_t argc, char *argv[]){
    struct ihex_packet pkt;
    uint8_t record_type;
    static uint8_t first_page_buffer[APP_SECTION_PAGE_SIZE];
    static bool first_page_dirty = false;
    
    if(argc != 2){
        return(1);
    }
    
    record_type = parse_intel_hex(argv[1], &pkt);
    if(record_type == IHEX_ERROR){
        return(1);
    }else if(record_type == IHEX_DATA){
        if(pkt.addr == 0){
            // About to write to first page. Clear the page buffer
            memset(first_page_buffer, 0xFF, sizeof(first_page_buffer));
            
            // Erase the first flash page. If something goes wrong while programming, an invalid
            // app won't be able to boot accidentally.
            sp_erase_page(0);
        }
        
        if(pkt.addr < APP_SECTION_PAGE_SIZE){
            // writing to first page. Divert to the page buffer.
            // This page will be written to flash last once everything else went OK.
            memcpy(&first_page_buffer[pkt.addr], pkt.data, pkt.len);
            first_page_dirty = true;
        }else{
            // not the first page. Write directly to flash
            sp_write(pkt.data, pkt.len, pkt.addr);
        }
        
    }else if(record_type == IHEX_EOF){
        // Got EOF hex record. Flush remaining flash into memory
        
        if(first_page_dirty){
            // Commit first page
            sp_write(first_page_buffer, sizeof(first_page_buffer), 0);
            first_page_dirty = false;
        }
        sp_flush();
        
    }else{
        // No action necessary for other records
    }
    return(0);
}
