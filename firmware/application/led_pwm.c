#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#include <avr/io.h>

#include <board.h>
#include "led_pwm.h"

//--------------------------------------------------------------------------------------------------
void pwm_init(void){
    // Init TCD0
    TCD0.CTRLC = 0x00; // Turn off RGBW outputs
    TCD0.CTRLB = TC_WGMODE_SINGLESLOPE_gc | TC0_CCAEN_bm | TC0_CCBEN_bm | TC0_CCCEN_bm | TC0_CCDEN_bm;
    TCD0.CTRLD = 0x00;
    TCD0.CTRLE = TC_BYTEM_NORMAL_gc;
    
    // Set RGBW to Off
    TCD0.CCA = 0;
    TCD0.CCB = 0;
    TCD0.CCC = 0;
    TCD0.CCD = 0;
    
    // Start timer
    TCD0.CTRLA = TC_CLKSEL_DIV1_gc;
}

//--------------------------------------------------------------------------------------------------
void pwm_uninit(void){
    TCD0.CTRLA = TC_CLKSEL_OFF_gc;
    TCD0.CTRLC = 0x00; // Turn off RGBW outputs
}

//--------------------------------------------------------------------------------------------------
void pwm_set_value(rgbw_t *rgbw){
    // Write to double-buffered register so that change mid-period doesn't cause flickering
    TCD0.CCABUF = rgbw->r;
    TCD0.CCBBUF = rgbw->g;
    TCD0.CCCBUF = rgbw->b;
    TCD0.CCDBUF = rgbw->w;
}

//--------------------------------------------------------------------------------------------------
void pwm_get_value(rgbw_t *rgbw){
    rgbw->r = TCD0.CCA;
    rgbw->g = TCD0.CCB;
    rgbw->b = TCD0.CCC;
    rgbw->w = TCD0.CCD;
}
