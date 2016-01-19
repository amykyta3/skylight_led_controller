
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/fuse.h>

#include <cli.h>
#include <uart_io.h>
#include <bt_rn42.h>
#include <board.h>

#define F_CPU 32000000UL
#include <util/delay.h>

//--------------------------------------------------------------------------------------------------
void blink_n(int n){
    int count = n;
    while(count){
        PORTA.OUTSET = P_LED_bm;
        _delay_ms(250);
        PORTA.OUTCLR = P_LED_bm;
        _delay_ms(250);
        count--;
    }
}
//--------------------------------------------------------------------------------------------------
void err(int n){
    while(1){
        _delay_ms(2000);
        blink_n(n);
    }
}

//--------------------------------------------------------------------------------------------------
int main(void){
    PORTA.OUTCLR = P_LED_bm;
    
//    err(4);
    _delay_ms(250);
    uart_init();
    
    // Enable interrupts
    PMIC.CTRL = PMIC_HILVLEN_bm;
    sei();
    
    cli_echo_off();
    cli_print_prompt();
    
    while(1){
        char c;
        PORTA.OUTTGL = P_LED_bm;
        c = uart_getc();
        cli_process_char(c);
    }
}
