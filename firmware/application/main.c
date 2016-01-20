
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include <avr/io.h>
#include <avr/interrupt.h>

#include <cli.h>
#include <uart_io.h>
#include <board.h>

#include "led_pwm.h"

//--------------------------------------------------------------------------------------------------
int main(void){
    PORTA.OUTCLR = P_LED_bm;
    
    uart_init();
    pwm_init();
    
    // Enable interrupts
    PMIC.CTRL = PMIC_HILVLEN_bm;
    sei();
    
    cli_echo_off();
    cli_print_prompt();
    
    while(1){
        char c;
        c = uart_getc();
        cli_process_char(c);
    }
}
