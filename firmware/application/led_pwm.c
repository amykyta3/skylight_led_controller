#include <stdint.h>

#include <avr/io.h>

#include <board.h>
#include "led_pwm.h"

void pwm_init(void){
    // Init TCD0
    TCD0.CTRLC = 0x00; // Turn off RGBW outputs
    TCD0.CTRLB = TC_WGMODE_SINGLESLOPE_gc | TC0_CCAEN_bm | TC0_CCBEN_bm | TC0_CCCEN_bm | TC0_CCDEN_bm;
    TCD0.CTRLD = 0x00;
    TCD0.CTRLE = TC_BYTEM_NORMAL_gc;
    
    // Set RGBW to Off
    pwm_set_value(0,0,0,0);
    
    // Start timer
    TCD0.CTRLA = TC_CLKSEL_DIV1_gc;
}

void pwm_uninit(void){
    TCD0.CTRLA = TC_CLKSEL_OFF_gc;
    TCD0.CTRLC = 0x00; // Turn off RGBW outputs
}

void pwm_set_value(uint16_t red, uint16_t green, uint16_t blue, uint16_t white){
    
    // Red
    TCD0.CCAL = (red & 0xFF);
    TCD0.CCAH = (red >> 8);
    
    // Green
    TCD0.CCBL = (green & 0xFF);
    TCD0.CCBH = (green >> 8);
    
    // Blue
    TCD0.CCCL = (blue & 0xFF);
    TCD0.CCCH = (blue >> 8);
    
    // White
    TCD0.CCDL = (white & 0xFF);
    TCD0.CCDH = (white >> 8);
}
