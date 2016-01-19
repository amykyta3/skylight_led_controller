#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include <avr/io.h>
#include <avr/interrupt.h>

#include <cli_commands.h>
#include <uart_io.h>
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
int cmd_id(uint8_t argc, char *argv[]){
    cli_puts("APP");
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
    PROTECTED_WRITE(RST.CTRL, RST_SWRST_bm);
    return(0);
}

