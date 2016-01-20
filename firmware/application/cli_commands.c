#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>

#include <avr/io.h>
#include <avr/interrupt.h>

#include <cli.h>
#include <cli_commands.h>
#include <uart_io.h>
#include <board.h>

#include "led_pwm.h"

//==================================================================================================
static uint16_t xtou16(char *s){
    uint16_t n = 0;
    while(*s){
        uint8_t nib;
        if(isdigit(*s)){
            nib = *s - '0';
        }else if((*s >= 'A') && (*s <= 'F')){
            nib = *s - 'A' + 10;
        }else if((*s >= 'a') && (*s <= 'f')){
            nib = *s - 'a' + 10;
        }else{
            return(n);
        }
        n <<= 4;
        n += nib;
        s++;
    }
    return(n);
}

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
    if(argc != 2) return(1);
    
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
int cmd_echo(uint8_t argc, char *argv[]){
    if(argc != 2) return(1);
    
    if(argv[1][0] == '1'){
        cli_echo_on();
    }else if(argv[1][0] == '0'){
        cli_echo_off();
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

//--------------------------------------------------------------------------------------------------
int cmd_rgbw(uint8_t argc, char *argv[]){
    uint16_t r, g, b, w;
    if(argc != 5) return(1);
    
    r = xtou16(argv[1]);
    g = xtou16(argv[2]);
    b = xtou16(argv[3]);
    w = xtou16(argv[4]);
    pwm_set_value(r,g,b,w);
    return(0);
}

