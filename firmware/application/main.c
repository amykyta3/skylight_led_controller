
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include <avr/io.h>
#include <avr/interrupt.h>

#include <cli.h>
#include <uart_io.h>
#include <event_queue.h>
#include <rtc.h>

#include <board.h>

#include "led_pwm.h"

//--------------------------------------------------------------------------------------------------
int main(void){
    PORTA.OUTCLR = P_LED_bm;
    
    event_init();
    uart_init();
    pwm_init();
    rtc_init();
    
    // Enable interrupts
    PMIC.CTRL = PMIC_HILVLEN_bm | PMIC_MEDLVLEN_bm | PMIC_LOLVLEN_bm;
    sei();
    
    cli_echo_off();
    cli_print_prompt();
    
    event_StartHandler(); // Does not return
}

//--------------------------------------------------------------------------------------------------
void onIdle(void){
    
    if(uart_rdcount() > 0){
        char c;
        c = uart_getc();
        cli_process_char(c);
    }
}
