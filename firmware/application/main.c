
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
#include "led_transitions.h"
#include "debug.h"
#include "eeprom_config.h"
#include "light_switch.h"

//--------------------------------------------------------------------------------------------------
int main(void){
    PORTA.OUTCLR = P_LED_bm;
    
    event_init();
    uart_init();
    pwm_init();
    rtc_init();
    debug_init();
    eecfg_init();
    light_switch_init();
    transition_init();
    
    // Enable interrupts
    PMIC.CTRL = PMIC_HILVLEN_bm | PMIC_MEDLVLEN_bm | PMIC_LOLVLEN_bm;
    sei();
    
    cli_echo_off();
    cli_print_prompt();
    
    event_StartHandler(); // Does not return
}

//--------------------------------------------------------------------------------------------------
void onIdle(void){
    char buf[16];
    size_t n_bytes;
    
    if(uart_rdcount() > 0){
        char c;
        c = uart_getc();
        cli_process_char(c);
    }
    
    n_bytes = debug_get_chunk(buf, sizeof(buf));
    if(n_bytes){
        uart_write(buf, n_bytes);
    }
}
