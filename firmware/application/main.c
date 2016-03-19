
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
#include "veml6040.h"

void start_error_led(uint8_t err_no);

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
    veml6040_init();
    
    // Enable interrupts
    PMIC.CTRL = PMIC_HILVLEN_bm | PMIC_MEDLVLEN_bm | PMIC_LOLVLEN_bm;
    sei();
    
    // Start error blinker to indicate time isn't set
    start_error_led(1);
    
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

//--------------------------------------------------------------------------------------------------
static timer_t error_led_timer;
static uint8_t current_err_no;
static uint8_t err_loop_count;

static void error_led_callback(void *data){
    if((err_loop_count % 2) == 0){
        if(current_err_no == err_loop_count/2){
            // blinked enough times. Reset
            err_loop_count = 0;
            return;
        } else {
            PORTA.OUTSET = P_LED_bm;
        }
    }else{
        PORTA.OUTCLR = P_LED_bm;
    }
    err_loop_count++;
}

void start_error_led(uint8_t err_no){
    struct timerctl t;
    current_err_no = err_no;
    err_loop_count = 0;
    
    t.interval = 32; // 1/2 sec
    t.repeat = true;
    t.callback = error_led_callback;
    t.callback_data = NULL;
    timer_start(&error_led_timer, &t);
}

void stop_error_led(void){
    timer_stop(&error_led_timer);
    PORTA.OUTCLR = P_LED_bm;
}
