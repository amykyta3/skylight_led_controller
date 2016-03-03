#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#include <avr/io.h>

#include <board.h>
#include "led_pwm.h"

#include <fixedpt.h>

static rgbw_t current_rgbw;
//--------------------------------------------------------------------------------------------------
void pwm_init(void){
    // Init TCD0
    TCD0.CTRLC = 0x00; // Turn off RGBW outputs
    TCD0.CTRLB = TC_WGMODE_SINGLESLOPE_gc | TC0_CCAEN_bm | TC0_CCBEN_bm | TC0_CCCEN_bm | TC0_CCDEN_bm;
    TCD0.CTRLD = 0x00;
    TCD0.CTRLE = TC_BYTEM_NORMAL_gc;
    
    current_rgbw.r = 0;
    current_rgbw.g = 0;
    current_rgbw.b = 0;
    current_rgbw.w = 0;
    
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
static uint16_t lightness2pwm(uint16_t L){
    uint16_t L_2;
    uint16_t L_3;
    // Convert lightness to PWM value
    // Y = 0.5*L^2 + 0.5^L^3 (where Y and L are from 0.0 to 1.0)
    // ... is a surprisingly close approximation to the CIELAB lightness formula
    
    // Interpret L as Q16 fixed point
    L_2 = mpy_Q16(L,L);
    L_3 = mpy_Q16(L_2,L);
    L_2 >>= 1;
    L_3 >>= 1;
    return(L_2 + L_3);
}

//--------------------------------------------------------------------------------------------------
void pwm_set_value(rgbw_t *rgbw){
    // Save lightness value
    current_rgbw.r = rgbw->r;
    current_rgbw.g = rgbw->g;
    current_rgbw.b = rgbw->b;
    current_rgbw.w = rgbw->w;
    
    // Write to double-buffered register so that change mid-period doesn't cause flickering
    TCD0.CCABUF = lightness2pwm(current_rgbw.r);
    TCD0.CCBBUF = lightness2pwm(current_rgbw.g);
    TCD0.CCCBUF = lightness2pwm(current_rgbw.b);
    TCD0.CCDBUF = lightness2pwm(current_rgbw.w);
}

//--------------------------------------------------------------------------------------------------
void pwm_get_value(rgbw_t *rgbw){
    rgbw->r = current_rgbw.r;
    rgbw->g = current_rgbw.g;
    rgbw->b = current_rgbw.b;
    rgbw->w = current_rgbw.w;
}
